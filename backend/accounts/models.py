from typing import Any

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class Role(models.TextChoices):
    STUDENT = "ROLE_STUDENT", "Öğrenci"
    ADMIN = "ROLE_ADMIN", "Yönetici"


class UserManager(BaseUserManager):
    """E-posta ile giriş yapan kullanıcıları oluşturur."""

    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra_fields: Any) -> "User":
        if not email:
            raise ValueError("E-posta adresi zorunludur.")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields: Any) -> "User":
        extra_fields.setdefault("role", Role.STUDENT)
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str | None = None, **extra_fields: Any) -> "User":
        extra_fields.setdefault("role", Role.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Sistemdeki tüm kullanıcılar. Yetki kararları `role` alanına göre verilir."""

    username = None
    email = models.EmailField("e-posta", unique=True)
    role = models.CharField("rol", max_length=20, choices=Role.choices, default=Role.STUDENT)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    class Meta:
        verbose_name = "kullanıcı"
        verbose_name_plural = "kullanıcılar"

    def __str__(self) -> str:
        return self.email

    def has_role(self, role: Role) -> bool:
        return self.role == role

    @property
    def is_student(self) -> bool:
        return self.has_role(Role.STUDENT)

    @property
    def is_admin(self) -> bool:
        return self.has_role(Role.ADMIN)
