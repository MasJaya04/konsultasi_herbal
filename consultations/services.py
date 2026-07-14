import logging
import re
import time

import requests
from django.conf import settings
from django.db.models import Q

from catalog.models import Product
from config.middleware import RequestLoggerAdapter
from knowledge.models import KnowledgeEntry

logger = logging.getLogger("consultations")

COMMON_WORDS = {
    "dan",
    "atau",
    "yang",
    "untuk",
    "dengan",
    "pada",
    "dari",
    "ke",
    "di",
    "apakah",
    "saya",
    "kamu",
    "tau",
    "tahu",
    "sekarang",
    "adalah",
    "ingin",
    "mau",
    "tanya",
    "tentang",
    "produk",
    "herbal",
}

INTENT_KEYWORDS = {
    "benefit": {"untuk apa", "manfaat", "fungsi", "khasiat", "kegunaan", "indikasi"},
    "usage": {"cara pakai", "aturan pakai", "dosis", "minum", "konsumsi"},
    "warning": {"kontraindikasi", "pantangan", "hati hati", "perhatian", "alergi", "ibu hamil", "menyusui"},
    "profile": {"apa itu", "profil", "deskripsi", "informasi", "komposisi", "kandungan"},
}

FOLLOW_UP_HINTS = {
    "bagaimana",
    "gimana",
    "aman",
    "boleh",
    "bisakah",
    "apakah",
    "efek",
    "samping",
    "aturan",
    "pakai",
    "dosis",
    "manfaat",
    "fungsi",
    "khasiat",
    "komposisi",
    "kandungan",
    "minum",
    "konsumsi",
}

GREETING_WORDS = {
    "hai",
    "halo",
    "hi",
    "hello",
    "pagi",
    "siang",
    "sore",
    "malam",
    "permisi",
}

FILLER_WORDS = {
    "aku",
    "saya",
    "mau",
    "ingin",
    "tanya",
    "bertanya",
    "dong",
    "nih",
    "ini",
    "ya",
    "yah",
    "kak",
    "min",
    "bro",
    "sis",
    "produk",
}

WORD_NORMALIZATION_MAP = {
    "gmn": "gimana",
    "gmna": "gimana",
    "gmnya": "gimananya",
    "utk": "untuk",
    "utk.": "untuk",
    "dr": "dari",
    "dg": "dengan",
    "dgn": "dengan",
    "sy": "saya",
    "aq": "aku",
    "ni": "ini",
    "nih": "ini",
    "brp": "berapa",
    "brapa": "berapa",
    "tp": "tapi",
    "pdhl": "padahal",
    "ga": "tidak",
    "gak": "tidak",
    "nggak": "tidak",
}

PRODUCT_FAMILY_ALIASES = {
    "bery la": "beryla",
    "deto green": "detogreen",
    "g z p": "gzp",
}

PRODUCT_NAME_ALIASES = {
    "gzp": "gerd zero pro",
}

PRODUCT_LIST_HINTS = {
    "apa saja",
    "ada apa saja",
    "produk apa saja",
    "varian",
    "list",
    "daftar",
    "semua produk",
    "ada banyak",
}

DEFAULT_CLARIFICATION_OPTIONS = [
    "Detogreen",
    "Beryla",
    "Gerd Zero Pro",
]

GENERIC_PRODUCT_TOKENS = {
    "produk",
    "herbal",
    "oil",
    "tea",
    "honey",
    "baby",
    "mom",
}


def _normalize_text(value):
    return re.sub(r"[^a-zA-Z0-9]+", " ", (value or "").lower()).strip()


def _normalize_tokens(text):
    return [
        token
        for token in re.findall(r"[a-zA-Z0-9]+", text.lower())
        if token and token not in COMMON_WORDS and len(token) > 1
    ]


def _contains_normalized_phrase(normalized_text, normalized_phrase):
    if not normalized_text or not normalized_phrase:
        return False
    return f" {normalized_phrase} " in f" {normalized_text} "


def preprocess_prompt(prompt):
    compact_prompt = re.sub(r"\s+", " ", (prompt or "").strip())
    if not compact_prompt:
        return ""
    lowered_prompt = compact_prompt.lower()
    for source, target in PRODUCT_FAMILY_ALIASES.items():
        lowered_prompt = re.sub(rf"\b{re.escape(source)}\b", target, lowered_prompt)
    for source, target in PRODUCT_NAME_ALIASES.items():
        lowered_prompt = re.sub(rf"\b{re.escape(source)}\b", target, lowered_prompt)
    normalized_tokens = []
    for raw_token in lowered_prompt.split(" "):
        token = re.sub(r"(^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$)", "", raw_token.lower())
        replacement = WORD_NORMALIZATION_MAP.get(token, token)
        normalized_tokens.append(replacement or token)
    return " ".join(token for token in normalized_tokens if token).strip()


def _detect_intent(prompt):
    normalized_prompt = _normalize_text(prompt)
    prompt_tokens = set(_normalize_tokens(prompt))
    intent = "general"
    for intent_name, keywords in INTENT_KEYWORDS.items():
        if any(keyword in normalized_prompt for keyword in keywords):
            return intent_name
    if normalized_prompt and all(token in GREETING_WORDS.union(FILLER_WORDS) for token in normalized_prompt.split()):
        return "greeting"
    if "produk" in normalized_prompt and not prompt_tokens:
        return "ambiguous_product"
    if not prompt_tokens and normalized_prompt:
        return "ambiguous"
    if prompt_tokens.intersection(FOLLOW_UP_HINTS):
        intent = "follow_up"
    return intent


def _score_text(query, text):
    query_tokens = _normalize_tokens(query)
    haystack = text.lower()
    unique_score = sum(3 for token in set(query_tokens) if token in haystack)
    phrase_bonus = 5 if query.strip().lower() in haystack else 0
    return unique_score + phrase_bonus


def _rank_knowledge_entry(prompt, entry):
    normalized_prompt = _normalize_text(prompt)
    category_title = _normalize_text(f"{entry.category.name} {entry.title}")
    intent_score = 0
    if any(term in normalized_prompt for term in ["untuk apa", "manfaat", "fungsi", "khasiat", "kegunaan"]):
        if any(term in category_title for term in ["manfaat", "fungsi", "khasiat", "kegunaan"]):
            intent_score = 40
    elif any(term in normalized_prompt for term in ["apa itu", "tau", "tahu", "kenal", "profil", "informasi", "jelaskan"]):
        if any(term in category_title for term in ["profil", "deskripsi", "apa itu"]):
            intent_score = 50
    elif any(term in normalized_prompt for term in ["cara pakai", "aturan pakai", "dosis", "minum", "konsumsi"]):
        if any(term in category_title for term in ["aturan pakai", "cara pakai", "dosis", "konsumsi"]):
            intent_score = 50
    elif any(term in normalized_prompt for term in ["kontraindikasi", "pantangan", "hati hati", "perhatian", "ibu hamil", "menyusui", "alergi"]):
        if any(term in category_title for term in ["kontraindikasi", "perhatian", "pantangan"]):
            intent_score = 50
    elif any(term in category_title for term in ["profil", "deskripsi"]):
        intent_score = 5
    return (
        intent_score
        + _score_text(prompt, entry.title) * 4
        + _score_text(prompt, entry.keywords) * 3
        + _score_text(prompt, entry.question) * 2
        + _score_text(prompt, entry.answer)
    )


def _rank_product(prompt, product):
    return (
        _score_text(prompt, product.name) * 4
        + _score_text(prompt, product.benefits) * 3
        + _score_text(prompt, product.description) * 2
        + _score_text(prompt, product.usage_instructions)
        + _score_text(prompt, product.contraindications)
    )


def _find_referenced_products(prompt, active_product=None):
    normalized_prompt = _normalize_text(prompt)
    prompt_tokens = set(_normalize_tokens(prompt))
    matched_products = []
    for product in Product.objects.filter(is_active=True).only("id", "name"):
        normalized_parts = _get_product_aliases(product)
        if any(
            part and (
                _contains_normalized_phrase(normalized_prompt, part)
                if " " in part
                else part in prompt_tokens
            )
            for part in normalized_parts
        ):
            matched_products.append(product)
    if active_product:
        return [product for product in matched_products if product.id != active_product.id]
    return matched_products


def find_prompt_product(prompt):
    normalized_prompt = _normalize_text(prompt)
    prompt_tokens = set(_normalize_tokens(prompt))
    scored_products = []
    for product in Product.objects.filter(is_active=True).select_related("category"):
        names = _get_product_aliases(product)
        matched_names = [
            name
            for name in names
            if name and (
                _contains_normalized_phrase(normalized_prompt, name)
                if " " in name
                else name in prompt_tokens
            )
        ]
        if matched_names:
            scored_products.append((product, max(len(name) for name in matched_names)))
    if not scored_products:
        return None
    return sorted(scored_products, key=lambda item: item[1], reverse=True)[0][0]


def _get_product_aliases(product):
    normalized_name = _normalize_text(product.name)
    normalized_slug = _normalize_text(product.slug)
    aliases = {normalized_name, normalized_slug}
    aliases.update(_normalize_text(part) for part in re.split(r"[/()|,]+", product.name))
    name_tokens = _normalize_tokens(product.name)
    aliases.update(token for token in name_tokens if len(token) >= 3)
    aliases.update(_build_product_alias_variants(name_tokens))
    return {alias for alias in aliases if alias}


def _build_product_alias_variants(name_tokens):
    aliases = set()
    if not name_tokens:
        return aliases
    joined_name = " ".join(name_tokens)
    aliases.add(joined_name)
    if len(name_tokens) >= 2:
        acronym = "".join(token[0] for token in name_tokens if token)
        if len(acronym) >= 2:
            aliases.add(acronym)
    meaningful_tokens = [token for token in name_tokens if token not in GENERIC_PRODUCT_TOKENS]
    if meaningful_tokens:
        aliases.add(" ".join(meaningful_tokens))
        if len(meaningful_tokens) >= 2:
            aliases.add("".join(meaningful_tokens))
            acronym = "".join(token[0] for token in meaningful_tokens if token)
            if len(acronym) >= 2:
                aliases.add(acronym)
    primary_tokens = meaningful_tokens[:3] if meaningful_tokens else name_tokens[:3]
    if len(primary_tokens) >= 2:
        aliases.add(" ".join(primary_tokens))
    return {_normalize_text(alias) for alias in aliases if alias}


def find_product_family(prompt):
    normalized_prompt = _normalize_text(prompt)
    family_products = {}
    for product in Product.objects.filter(is_active=True).only("id", "name"):
        normalized_name = _normalize_text(product.name)
        family = normalized_name.split(" ", 1)[0] if normalized_name else ""
        if family and _contains_normalized_phrase(normalized_prompt, family):
            family_products.setdefault(family, []).append(product)
    matched_families = [(family, products) for family, products in family_products.items() if len(products) > 1]
    if not matched_families:
        return None, []
    matched_families.sort(key=lambda item: (len(item[0]), len(item[1])), reverse=True)
    return matched_families[0]


def _is_product_list_request(prompt):
    normalized_prompt = _normalize_text(prompt)
    return any(hint in normalized_prompt for hint in PRODUCT_LIST_HINTS)


def _should_reuse_active_product(prompt):
    normalized_prompt = _normalize_text(prompt)
    if "produk ini" in normalized_prompt or "produk itu" in normalized_prompt or "produk tersebut" in normalized_prompt:
        return True
    return "produk" not in normalized_prompt


def _resolve_specific_product_from_family(prompt, family, family_products):
    prompt_tokens = set(_normalize_tokens(prompt))
    family_token = _normalize_text(family)
    scored_products = []
    for product in family_products:
        product_tokens = [
            token
            for token in _normalize_tokens(product.name)
            if token not in {"produk", "herbal"} and token != family_token
        ]
        score = len(set(product_tokens).intersection(prompt_tokens))
        scored_products.append((product, score))
    scored_products.sort(key=lambda item: item[1], reverse=True)
    if not scored_products or scored_products[0][1] == 0:
        return None
    if len(scored_products) > 1 and scored_products[0][1] == scored_products[1][1]:
        return None
    return scored_products[0][0]


def build_product_family_clarification(family, products):
    ordered_products = sorted(products, key=lambda item: item.name)
    options = ", ".join(product.name for product in ordered_products[:-1])
    if len(ordered_products) == 1:
        listed_names = ordered_products[0].name
    elif len(ordered_products) == 2:
        listed_names = f"{ordered_products[0].name} atau {ordered_products[1].name}"
    else:
        listed_names = f"{options}, atau {ordered_products[-1].name}"
    return f"Produk {family.title()} memiliki beberapa varian. Silakan pilih yang lebih spesifik: {listed_names}."


def build_product_list_answer(family, products):
    ordered_products = sorted(products, key=lambda item: item.name)
    if not ordered_products:
        return ""
    product_names = ", ".join(product.name for product in ordered_products[:-1])
    if len(ordered_products) == 1:
        listed_names = ordered_products[0].name
    elif len(ordered_products) == 2:
        listed_names = f"{ordered_products[0].name} dan {ordered_products[1].name}"
    else:
        listed_names = f"{product_names}, dan {ordered_products[-1].name}"
    return f"Produk {family.title()} yang tersedia saat ini ada {len(ordered_products)}, yaitu {listed_names}."


def build_product_options_source(products):
    return "OPTIONS:" + "|".join(product.name for product in sorted(products, key=lambda item: item.name)[:8])


def analyze_prompt(prompt, active_product=None, selected_product=None):
    processed_prompt = preprocess_prompt(prompt)
    intent = _detect_intent(processed_prompt)
    product_family, family_products = find_product_family(processed_prompt)
    if product_family and selected_product and any(item.id == selected_product.id for item in family_products):
        return {
            "processed_prompt": processed_prompt,
            "intent": intent,
            "product": selected_product,
            "needs_clarification": False,
            "clarification_message": "",
            "direct_answer": "",
            "direct_confidence": 0,
            "direct_source_summary": "",
            "direct_response_state": "answered",
            "direct_used_rag": False,
            "clarification_options": [],
        }
    if product_family and (_is_product_list_request(processed_prompt) or intent == "follow_up"):
        return {
            "processed_prompt": processed_prompt,
            "intent": "product_list",
            "product": None,
            "needs_clarification": False,
            "clarification_message": "",
            "direct_answer": build_product_list_answer(product_family, family_products),
            "direct_confidence": 0.92,
            "direct_source_summary": build_product_options_source(family_products),
            "direct_response_state": "answered",
            "direct_used_rag": False,
            "clarification_options": [],
        }
    if product_family and len(family_products) > 1:
        specific_family_product = _resolve_specific_product_from_family(processed_prompt, product_family, family_products)
        if specific_family_product:
            return {
                "processed_prompt": processed_prompt,
                "intent": intent,
                "product": specific_family_product,
                "needs_clarification": False,
                "clarification_message": "",
                "direct_answer": "",
                "direct_confidence": 0,
                "direct_source_summary": "",
                "direct_response_state": "answered",
                "direct_used_rag": False,
                "clarification_options": [],
            }
        return {
            "processed_prompt": processed_prompt,
            "intent": "family_clarification",
            "product": None,
            "needs_clarification": True,
            "clarification_message": build_product_family_clarification(product_family, family_products),
            "direct_answer": "",
            "direct_confidence": 0,
            "direct_source_summary": "",
            "direct_response_state": "answered",
            "direct_used_rag": False,
            "clarification_options": [product.name for product in sorted(family_products, key=lambda item: item.name)],
        }
    explicit_product = find_prompt_product(processed_prompt)
    if explicit_product:
        return {
            "processed_prompt": processed_prompt,
            "intent": intent,
            "product": explicit_product,
            "needs_clarification": False,
            "clarification_message": "",
            "direct_answer": "",
            "direct_confidence": 0,
            "direct_source_summary": "",
            "direct_response_state": "answered",
            "direct_used_rag": False,
            "clarification_options": [],
        }
    if selected_product:
        return {
            "processed_prompt": processed_prompt,
            "intent": intent,
            "product": selected_product,
            "needs_clarification": False,
            "clarification_message": "",
            "direct_answer": "",
            "direct_confidence": 0,
            "direct_source_summary": "",
            "direct_response_state": "answered",
            "direct_used_rag": False,
            "clarification_options": [],
        }
    if active_product and intent in {"follow_up", "benefit", "usage", "warning", "profile"} and _should_reuse_active_product(processed_prompt):
        return {
            "processed_prompt": processed_prompt,
            "intent": intent,
            "product": active_product,
            "needs_clarification": False,
            "clarification_message": "",
            "direct_answer": "",
            "direct_confidence": 0,
            "direct_source_summary": "",
            "direct_response_state": "answered",
            "direct_used_rag": False,
            "clarification_options": [],
        }
    if intent == "greeting":
        return {
            "processed_prompt": processed_prompt,
            "intent": intent,
            "product": None,
            "needs_clarification": True,
            "clarification_message": "Halo, saya siap membantu. Silakan sebutkan nama produk herbal yang ingin Anda tanyakan, misalnya Detogreen, Beryla, atau Gerd Zero Pro.",
            "direct_answer": "",
            "direct_confidence": 0,
            "direct_source_summary": "",
            "direct_response_state": "answered",
            "direct_used_rag": False,
            "clarification_options": DEFAULT_CLARIFICATION_OPTIONS,
        }
    return {
        "processed_prompt": processed_prompt,
        "intent": intent,
        "product": None,
        "needs_clarification": True,
        "clarification_message": "Silakan sebutkan nama produk herbal yang ingin Anda tanyakan terlebih dahulu, misalnya Detogreen, Beryla, atau Gerd Zero Pro.",
        "direct_answer": "",
        "direct_confidence": 0,
        "direct_source_summary": "",
        "direct_response_state": "answered",
        "direct_used_rag": False,
        "clarification_options": DEFAULT_CLARIFICATION_OPTIONS,
    }


def find_relevant_context(prompt, product=None):
    knowledge_queryset = KnowledgeEntry.objects.filter(status=KnowledgeEntry.Status.PUBLISHED).select_related("category", "product")
    product_queryset = Product.objects.filter(is_active=True).select_related("category")
    scoped_knowledge_entries = list(
        knowledge_queryset.filter(Q(product=product) | Q(product__isnull=True)) if product else knowledge_queryset
    )
    scoped_products = list(product_queryset.filter(pk=product.pk)) if product else list(product_queryset)
    ranked_knowledge = sorted(
        [(entry, _rank_knowledge_entry(prompt, entry)) for entry in scoped_knowledge_entries],
        key=lambda item: item[1],
        reverse=True,
    )
    ranked_products = sorted(
        [(candidate, _rank_product(prompt, candidate)) for candidate in scoped_products],
        key=lambda item: item[1],
        reverse=True,
    )
    selected_entries = [entry for entry, score in ranked_knowledge if score > 0][: settings.CONSULTATION_CONTEXT_LIMIT]
    selected_products = [candidate for candidate, score in ranked_products if score > 0][: settings.CONSULTATION_CONTEXT_LIMIT]
    if product and not selected_entries:
        fallback_ranked_knowledge = sorted(
            [(entry, _rank_knowledge_entry(prompt, entry)) for entry in knowledge_queryset],
            key=lambda item: item[1],
            reverse=True,
        )
        selected_entries = [entry for entry, score in fallback_ranked_knowledge if score > 0][: settings.CONSULTATION_CONTEXT_LIMIT]
    return selected_entries, selected_products


def build_prompt(prompt, entries, products):
    context_parts = []
    for entry in entries[: settings.CONSULTATION_CONTEXT_LIMIT]:
        entry_parts = [f"Judul: {entry.title}"]
        if entry.question:
            entry_parts.append(f"Pertanyaan referensi: {entry.question}")
        entry_parts.append(f"Jawaban referensi: {entry.answer}")
        context_parts.append("\n".join(entry_parts))
    for product in products[: settings.CONSULTATION_CONTEXT_LIMIT]:
        product_parts = [f"Produk: {product.name}"]
        if product.description:
            product_parts.append(f"Deskripsi: {product.description}")
        if product.benefits:
            product_parts.append(f"Manfaat: {product.benefits}")
        if product.usage_instructions:
            product_parts.append(f"Aturan pakai: {product.usage_instructions}")
        if product.contraindications:
            product_parts.append(f"Kontraindikasi: {product.contraindications}")
        context_parts.append("\n".join(product_parts))
    context_block = "\n\n".join(context_parts)
    return (
        "Jawab dalam bahasa Indonesia hanya berdasarkan konteks. "
        "Jangan diagnosis medis, jangan menambah fakta di luar konteks, dan jika konteks tidak cukup jawab persis: TIDAK_CUKUP_KONTEKS.\n\n"
        f"Konteks: {context_block}\nPertanyaan: {prompt}\nJawaban:"
    )


def build_source_summary(entries, products):
    source_labels = [f"KB: {entry.title}" for entry in entries]
    source_labels.extend([f"Produk: {product.name}" for product in products])
    return " | ".join(source_labels[:6])


def request_ollama_response(compiled_prompt, request=None):
    adapter = RequestLoggerAdapter(
        logger,
        {
            "request_id": getattr(request, "request_id", ""),
            "user_id": getattr(getattr(request, "user", None), "id", ""),
            "context": "ollama_request",
        },
    )
    payload = {
        "model": settings.OLLAMA_MODEL,
        "prompt": compiled_prompt,
        "stream": False,
        "think": settings.OLLAMA_THINK,
        "options": {
            "num_predict": settings.OLLAMA_NUM_PREDICT,
            "temperature": 0.2,
        },
    }
    adapter.info(f"Using Ollama model: {settings.OLLAMA_MODEL}")
    last_error = None
    retry_count = max(1, settings.OLLAMA_REQUEST_RETRIES)
    for attempt in range(retry_count):
        try:
            response = requests.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=settings.OLLAMA_TIMEOUT_SECONDS,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()
        except requests.RequestException as exc:
            last_error = exc
            adapter.error(str(exc))
            if attempt < retry_count - 1:
                time.sleep(2 ** attempt)
    raise last_error


def generate_consultation_answer(prompt, product=None, request=None):
    entries, products = find_relevant_context(prompt, product=product)
    if not entries and not products:
        return {
            "answer": "",
            "confidence": 0,
            "used_rag": True,
            "knowledge_entries": [],
            "source_summary": "",
            "response_state": "fallback",
            "reason": "Sistem tidak menemukan konteks yang relevan di basis pengetahuan.",
        }
    compiled_prompt = build_prompt(prompt, entries, products)
    answer = request_ollama_response(compiled_prompt, request=request)
    if "TIDAK_CUKUP_KONTEKS" in answer:
        return {
            "answer": "",
            "confidence": 0,
            "used_rag": True,
            "knowledge_entries": entries,
            "source_summary": build_source_summary(entries, products),
            "response_state": "fallback",
            "reason": "Model tidak memiliki konteks yang cukup untuk menjawab.",
        }
    confidence = min(0.99, 0.45 + (len(entries) * 0.12) + (len(products) * 0.08))
    return {
        "answer": answer,
        "confidence": round(confidence, 2),
        "used_rag": True,
        "knowledge_entries": entries,
        "source_summary": build_source_summary(entries, products),
        "response_state": "answered",
        "reason": "",
    }
