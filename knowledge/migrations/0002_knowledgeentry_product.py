from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0001_initial"),
        ("knowledge", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="knowledgeentry",
            name="product",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="knowledge_entries", to="catalog.product"),
        ),
    ]
