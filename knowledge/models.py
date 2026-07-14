from django.conf import settings
from django.db import models
import re

from catalog.models import Product


class KnowledgeCategory(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class KnowledgeEntry(models.Model):
    class SourceType(models.TextChoices):
        FAQ = "faq", "FAQ"
        PRODUCT = "product", "Produk"
        SOP = "sop", "SOP"
        ARTICLE = "article", "Artikel"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draf"
        PUBLISHED = "published", "Terbit"

    class QualityStatus(models.TextChoices):
        STRONG = "strong", "Kuat"
        NEEDS_REVIEW = "needs_review", "Perlu ditinjau"
        WEAK = "weak", "Lemah"

    category = models.ForeignKey(KnowledgeCategory, on_delete=models.PROTECT, related_name="entries")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="knowledge_entries", null=True, blank=True)
    title = models.CharField(max_length=200)
    question = models.TextField(blank=True)
    answer = models.TextField()
    source_type = models.CharField(max_length=20, choices=SourceType.choices, default=SourceType.FAQ)
    keywords = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PUBLISHED)
    quality_status = models.CharField(max_length=20, choices=QualityStatus.choices, default=QualityStatus.NEEDS_REVIEW)
    review_note = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_knowledge_entries")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="knowledge_entries")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("title",)

    def __str__(self):
        return self.title


QUALITY_COMMON_WORDS = {
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
    "ingin",
    "mau",
    "tanya",
    "tentang",
    "produk",
    "herbal",
    "ini",
    "itu",
}


def _quality_tokens(text):
    return [
        token
        for token in re.findall(r"[a-zA-Z0-9]+", (text or "").lower())
        if token and token not in QUALITY_COMMON_WORDS and len(token) > 2
    ]


def _entry_matches_unanswered(entry, unanswered_question):
    entry_tokens = set(_quality_tokens(" ".join([entry.title, entry.question, entry.keywords, entry.answer])))
    question_tokens = set(_quality_tokens(unanswered_question.question))
    if not entry_tokens or not question_tokens:
        return False
    return len(entry_tokens.intersection(question_tokens)) >= 2


def refresh_knowledge_quality(*, product_ids=None, entry_ids=None):
    from consultations.models import AIResponseReview, UnansweredQuestion

    queryset = KnowledgeEntry.objects.select_related("product")
    if product_ids:
        queryset = queryset.filter(product_id__in=product_ids)
    if entry_ids:
        queryset = queryset.filter(pk__in=entry_ids)
    entries = list(queryset)
    if not entries:
        return 0
    unanswered_queryset = UnansweredQuestion.objects.filter(status=UnansweredQuestion.Status.OPEN)
    if product_ids:
        unanswered_queryset = unanswered_queryset.filter(product_id__in=product_ids)
    product_open_unanswered = {}
    for item in unanswered_queryset.select_related("product"):
        product_open_unanswered.setdefault(item.product_id, []).append(item)
    updated_count = 0
    for entry in entries:
        review_queryset = AIResponseReview.objects.filter(message__knowledge_entries=entry)
        has_incorrect = review_queryset.filter(verdict=AIResponseReview.Verdict.INCORRECT).exists()
        has_needs_revision = review_queryset.filter(verdict=AIResponseReview.Verdict.NEEDS_REVISION).exists()
        has_accurate = review_queryset.filter(verdict=AIResponseReview.Verdict.ACCURATE).exists()
        has_unanswered_signal = any(
            _entry_matches_unanswered(entry, unanswered)
            for unanswered in product_open_unanswered.get(entry.product_id, [])
        )
        new_status = entry.quality_status
        if has_incorrect:
            new_status = KnowledgeEntry.QualityStatus.WEAK
        elif has_needs_revision or has_unanswered_signal:
            new_status = KnowledgeEntry.QualityStatus.NEEDS_REVIEW
        elif has_accurate:
            new_status = KnowledgeEntry.QualityStatus.STRONG
        if new_status != entry.quality_status:
            entry.quality_status = new_status
            entry.save(update_fields=["quality_status", "updated_at"])
            updated_count += 1
    return updated_count
