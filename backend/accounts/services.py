import logging
import math
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from students.models import StudentProfile

from .exceptions import AccountLocked
from .models import LoginAttempt, LoginLock, Role, User

logger = logging.getLogger(__name__)


class LoginGuard:
    """Giriş denemelerini kaydeder, üst üste hatalı denemede e-postayı süreli kilitler."""

    def __init__(self, email: str, ip_address: str | None) -> None:
        self._email = email.strip().lower()
        self._ip_address = ip_address

    def ensure_not_locked(self) -> None:
        now = timezone.now()
        lock = LoginLock.objects.filter(email=self._email).first()
        if lock is not None and lock.is_locked(now):
            logger.warning("Kilitli hesaba giriş denemesi: %s (%s)", self._email, self._ip_address)
            raise AccountLocked(math.ceil((lock.locked_until - now).total_seconds() / 60))

    def record_failure(self) -> None:
        logger.warning("Başarısız giriş denemesi: %s (%s)", self._email, self._ip_address)
        self._log(succeeded=False)
        rules = settings.LOGIN_LOCK
        lock, _ = LoginLock.objects.get_or_create(email=self._email)
        lock.register_failure(timezone.now(), rules["MAX_FAILURES"], timedelta(minutes=rules["MINUTES"]))
        lock.save()

    def record_success(self) -> None:
        self._log(succeeded=True)
        LoginLock.objects.filter(email=self._email).delete()

    def _log(self, *, succeeded: bool) -> None:
        LoginAttempt.objects.create(email=self._email, ip_address=self._ip_address, succeeded=succeeded)


@transaction.atomic
def register_student(
    *, email: str, password: str, first_name: str, last_name: str, student_number: str
) -> User:
    """Veri setinde kayıtlı ve henüz hesabı olmayan öğrenci için hesap açar.

    Öğrenci profili admin'in içe aktardığı veri setinden gelir; kayıt yalnızca
    bu profili kullanıcıyla eşleştirir.
    """
    profile = (
        StudentProfile.objects.select_for_update()
        .filter(student_number=student_number.strip())
        .first()
    )
    if profile is None:
        raise ValidationError({"student_number": ["Öğrenci numarası öğrenci veri setinde bulunamadı."]})
    if profile.user_id is not None:
        raise ValidationError({"student_number": ["Bu öğrenci numarası için zaten bir hesap var."]})
    if User.objects.filter(email__iexact=email).exists():
        raise ValidationError({"email": ["Bu e-posta adresiyle kayıtlı bir hesap var."]})

    user = User.objects.create_user(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        role=Role.STUDENT,
    )
    profile.user = user
    profile.save(update_fields=["user", "updated_at"])
    return user
