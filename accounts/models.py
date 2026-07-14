from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        AI_TRAINER = "ai_trainer", "Pelatih AI"
        CUSTOMER = "customer", "Pengguna"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_ai_trainer(self):
        return self.role == self.Role.AI_TRAINER
