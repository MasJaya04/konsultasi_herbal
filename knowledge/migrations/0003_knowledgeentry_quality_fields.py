from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("knowledge", "0002_knowledgeentry_product"),
    ]

    operations = [
        migrations.AddField(
            model_name="knowledgeentry",
            name="quality_status",
            field=models.CharField(choices=[("strong", "Strong"), ("needs_review", "Needs Review"), ("weak", "Weak")], default="needs_review", max_length=20),
        ),
        migrations.AddField(
            model_name="knowledgeentry",
            name="review_note",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="knowledgeentry",
            name="reviewed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="knowledgeentry",
            name="reviewed_by",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="reviewed_knowledge_entries", to=settings.AUTH_USER_MODEL),
        ),
    ]
