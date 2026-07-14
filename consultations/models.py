from django.conf import settings
from django.db import models

from catalog.models import Product
from knowledge.models import KnowledgeEntry


class ConsultationSession(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Aktif"
        CLOSED = "closed", "Ditutup"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="consultation_sessions")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="consultation_sessions", null=True, blank=True)
    title = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)

    def __str__(self):
        return self.title

    @property
    def referenced_products(self):
        products = []
        seen_product_ids = set()
        for message in self.messages.all():
            if not message.product_id or message.product_id in seen_product_ids:
                continue
            seen_product_ids.add(message.product_id)
            products.append(message.product)
        return products

    @property
    def referenced_product_names(self):
        return [product.name for product in self.referenced_products]

    @property
    def latest_referenced_product(self):
        for message in reversed(list(self.messages.all())):
            if message.product_id:
                return message.product
        return self.product


class ConsultationMessage(models.Model):
    class Sender(models.TextChoices):
        USER = "user", "Pengguna"
        AI = "ai", "AI"

    class ResponseState(models.TextChoices):
        ANSWERED = "answered", "Terjawab"
        FALLBACK = "fallback", "Cadangan"

    session = models.ForeignKey(ConsultationSession, on_delete=models.CASCADE, related_name="messages")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="consultation_messages", null=True, blank=True)
    sender = models.CharField(max_length=10, choices=Sender.choices)
    content = models.TextField()
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    used_rag = models.BooleanField(default=False)
    response_state = models.CharField(max_length=20, choices=ResponseState.choices, default=ResponseState.ANSWERED)
    source_summary = models.TextField(blank=True)
    knowledge_entries = models.ManyToManyField(KnowledgeEntry, blank=True, related_name="consultation_messages")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)


class UnansweredQuestion(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Terbuka"
        REVIEWED = "reviewed", "Sudah ditinjau"
        RESOLVED = "resolved", "Selesai"

    session = models.ForeignKey(ConsultationSession, on_delete=models.CASCADE, related_name="unanswered_questions")
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="unanswered_questions")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="unanswered_questions", null=True, blank=True)
    question = models.TextField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    resolved_entry = models.ForeignKey(KnowledgeEntry, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)


class AIResponseReview(models.Model):
    class Verdict(models.TextChoices):
        ACCURATE = "accurate", "Akurat"
        NEEDS_REVISION = "needs_revision", "Perlu revisi"
        INCORRECT = "incorrect", "Tidak tepat"

    message = models.ForeignKey(ConsultationMessage, on_delete=models.CASCADE, related_name="reviews")
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="ai_reviews")
    verdict = models.CharField(max_length=20, choices=Verdict.choices)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)


class ActivityLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="activity_logs")
    action = models.CharField(max_length=120)
    target_type = models.CharField(max_length=120)
    target_id = models.CharField(max_length=120, blank=True)
    description = models.TextField()
    request_id = models.CharField(max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)


def create_activity_log(*, actor=None, action="", target_type="", target_id="", description="", request_id=""):
    return ActivityLog.objects.create(
        actor=actor,
        action=action,
        target_type=target_type,
        target_id=str(target_id or ""),
        description=description,
        request_id=request_id or "",
    )
