import re
from collections.abc import Callable
from typing import Any

from readers.ek16 import Ek16Data
from readers.parsing import is_turkish_nationality, normalize_tr

from ..context import ValidationContext
from ..types import Severity, ValidationIssue
from .base import BaseValidator

__all__ = ["StudentIdentityValidator", "normalize_tr"]


def _exact(value: Any) -> str:
    return str(value).strip()


def _text(value: Any) -> str:
    return normalize_tr(str(value))


def _letters_and_digits(value: Any) -> str:
    return re.sub(r"[\W_]+", "", normalize_tr(str(value)))


def _phone(value: Any) -> str:
    return re.sub(r"\D", "", str(value))[-10:]


def _nationality(value: Any) -> str:
    return "tc" if is_turkish_nationality(str(value)) else normalize_tr(str(value))


class StudentIdentityValidator(BaseValidator):
    """Belgedeki öğrenci bilgilerini giriş yapan öğrencinin veri setindeki kaydıyla karşılaştırır.

    Veri setinde boş olan bilgi karşılaştırılmaz.
    """

    code = "student_identity"
    description = "Öğrenci bilgilerinin veri setiyle uyuşması"

    # Ek-16 alanı, StudentProfile alanı, karşılaştırmadan önce uygulanan dönüşüm
    COMPARISONS: tuple[tuple[str, str, Callable[[Any], str]], ...] = (
        ("student_number", "student_number", _exact),
        ("student_full_name", "full_name", _text),
        ("national_id", "national_id", _exact),
        ("nationality", "nationality", _nationality),
        ("birth_date", "birth_date", _exact),
        ("home_address", "home_address", _letters_and_digits),
        ("previous_internship_days", "previous_internship_days", _exact),
        ("student_email", "email", _text),
        ("student_phone", "phone", _phone),
        ("health_status", "health_status", _exact),
    )

    def validate(self, data: Ek16Data, context: ValidationContext) -> list[ValidationIssue]:
        student = context.student
        if student is None:
            return [self._issue(None, "Belge sahibi öğrenci veri setinde bulunamadı.")]

        issues: list[ValidationIssue] = []
        for field_name, profile_field, normalize in self.COMPARISONS:
            document_value = getattr(data, field_name)
            record_value = getattr(student, profile_field)
            if document_value in (None, "") or record_value in (None, ""):
                continue
            if normalize(document_value) != normalize(record_value):
                label = Ek16Data.label_for(field_name)
                issues.append(self._issue(field_name, f"Belgedeki '{label}' öğrenci kaydıyla uyuşmuyor."))
        if data.department and normalize_tr(data.department) != normalize_tr(student.department):
            issues.append(
                self._issue(
                    "department",
                    "Belgedeki bölüm adı öğrenci kaydından farklı yazılmış.",
                    Severity.WARNING,
                )
            )
        return issues
