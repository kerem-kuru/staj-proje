from readers.ek16 import Ek16Data
from readers.parsing import normalize_tr

from ..context import ValidationContext
from ..types import Severity, ValidationIssue
from .base import BaseValidator

__all__ = ["StudentIdentityValidator", "normalize_tr"]


class StudentIdentityValidator(BaseValidator):
    """Belgedeki öğrenci bilgilerini öğrenci veri setiyle karşılaştırır."""

    code = "student_identity"
    description = "Öğrenci bilgilerinin veri setiyle uyuşması"

    def validate(self, data: Ek16Data, context: ValidationContext) -> list[ValidationIssue]:
        student = context.student
        if student is None:
            return [self._issue(None, "Belge sahibi öğrenci veri setinde bulunamadı.")]

        issues: list[ValidationIssue] = []
        if data.student_number and data.student_number.strip() != student.student_number:
            issues.append(self._issue("student_number", "Belgedeki öğrenci numarası sizin numaranızla uyuşmuyor."))
        if data.student_full_name and normalize_tr(data.student_full_name) != normalize_tr(student.full_name):
            issues.append(self._issue("student_full_name", "Belgedeki ad soyad öğrenci kaydıyla uyuşmuyor."))
        if data.national_id and student.national_id and data.national_id.strip() != student.national_id:
            issues.append(self._issue("national_id", "Belgedeki T.C. kimlik numarası öğrenci kaydıyla uyuşmuyor."))
        if data.department and normalize_tr(data.department) != normalize_tr(student.department):
            issues.append(
                self._issue(
                    "department",
                    "Belgedeki bölüm adı öğrenci kaydından farklı yazılmış.",
                    Severity.WARNING,
                )
            )
        return issues
