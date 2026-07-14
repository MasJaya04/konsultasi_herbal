from django.db import migrations


DEFAULT_USERS = [
    {
        "username": "nurjaya_admin",
        "first_name": "Nurjaya",
        "last_name": "Admin",
        "role": "admin",
        "is_staff": True,
        "is_superuser": True,
        "password": "pbkdf2_sha256$1200000$QTapJ5dqdZKUgq5hVqJFl6$zkc0G97CtzW8XAM2T4jQhk206+WjVjR7bPHtHddSmAA=",
    },
    {
        "username": "nurjaya_trainer",
        "first_name": "Nurjaya",
        "last_name": "Trainer",
        "role": "ai_trainer",
        "is_staff": False,
        "is_superuser": False,
        "password": "pbkdf2_sha256$1200000$ygERJpAcL2trlWdgof6Gvw$MAX6qR6n31veaqnCkCHFYcIjSatdNvBQdexPLjV1fDw=",
    },
    {
        "username": "nurjaya_customer",
        "first_name": "Nurjaya",
        "last_name": "Customer",
        "role": "customer",
        "is_staff": False,
        "is_superuser": False,
        "password": "pbkdf2_sha256$1200000$5NvczaaNFsJy14fGJ9LEOi$QtJ7LsLJYDK3uDc+ldoUgA19IusqAy9AN0qnSfrbU2Y=",
    },
]


def create_default_users(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    for data in DEFAULT_USERS:
        user, _ = User.objects.update_or_create(
            username=data["username"],
            defaults={
                "first_name": data["first_name"],
                "last_name": data["last_name"],
                "role": data["role"],
                "is_staff": data["is_staff"],
                "is_superuser": data["is_superuser"],
                "is_active": True,
                "password": data["password"],
            },
        )
        user.user_permissions.clear()
        user.groups.clear()


def remove_default_users(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.filter(username__in=[data["username"] for data in DEFAULT_USERS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_default_users, remove_default_users),
    ]
