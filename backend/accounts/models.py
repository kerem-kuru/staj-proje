from datetime import datetime, timedelta
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
    # Token'lara yazılır; artırıldığında o ana kadar verilmiş tüm token'lar geçersiz olur.
    token_version = models.PositiveIntegerField("token sürümü", default=0, editable=False)

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

    def revoke_tokens(self) -> None:
        self.token_version += 1
        self.save(update_fields=["token_version"])


class LoginAttempt(models.Model):
    """Giriş denemesi kaydı. Var olmayan e-postalar da yazıldığı için User'a bağlı değildir."""

    email = models.CharField("e-posta", max_length=254, db_index=True)
    ip_address = models.GenericIPAddressField("IP adresi", null=True, blank=True)
    succeeded = models.BooleanField("başarılı")
    created_at = models.DateTimeField("zaman", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "giriş denemesi"
        verbose_name_plural = "giriş denemeleri"

    def __str__(self) -> str:
        return f"{self.email} ({'başarılı' if self.succeeded else 'başarısız'})"


class LoginLock(models.Model):
    """Bir e-posta için üst üste hatalı deneme sayısı ve kilit süresi. Kaydı silmek kilidi açar."""

    email = models.CharField("e-posta", max_length=254, unique=True)
    failures = models.PositiveSmallIntegerField("hatalı deneme", default=0)
    locked_until = models.DateTimeField("kilit bitişi", null=True, blank=True)

    class Meta:
        verbose_name = "giriş kilidi"
        verbose_name_plural = "giriş kilitleri"

    def __str__(self) -> str:
        return self.email

    def is_locked(self, now: datetime) -> bool:
        return self.locked_until is not None and now < self.locked_until

    def register_failure(self, now: datetime, max_failures: int, lock_for: timedelta) -> None:
        if self.locked_until is not None and now >= self.locked_until:
            self.failures, self.locked_until = 0, None  # süresi dolan kilit sayacı sıfırlar
        self.failures += 1
        if self.failures >= max_failures:
            self.locked_until = now + lock_for
