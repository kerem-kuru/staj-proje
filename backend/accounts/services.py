from django.db import transaction
from rest_framework.exceptions import ValidationError

from students.models import StudentProfile

from .models import Role, User


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
