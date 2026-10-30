from readers.ek16 import Ek16Data

from ..context import ValidationContext
from ..types import ValidationIssue
from .base import BaseValidator


class SignatureValidator(BaseValidator):
    code = "signatures"
    description = "Öğrenci imzası ile firma kaşe/imzasının bulunması"

    def validate(self, data: Ek16Data, context: ValidationContext) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        if not data.has_student_signature:
            issues.append(self._issue("has_student_signature", "Belgede öğrenci imzası bulunamadı."))
        if not data.has_company_stamp:
            issues.append(self._issue("has_company_stamp", "Belgede firma kaşesi ve yetkili imzası bulunamadı."))
        return issues
