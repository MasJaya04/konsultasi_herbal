from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("catalog", "0001_initial"),
        ("consultations", "0003_activitylog"),
    ]

    operations = [
        migrations.AddField(
            model_name="consultationsession",
            name="product",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="consultation_sessions", to="catalog.product"),
        ),
        migrations.AddField(
            model_name="unansweredquestion",
            name="product",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="unanswered_questions", to="catalog.product"),
        ),
    ]
