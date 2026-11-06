from readers.ek16 import Ek16Data

from ..context import ValidationContext
from ..types import ValidationIssue
from .base import BaseValidator


class SignatureValidator(BaseValidator):
    """İşveren kısmı kaşe ve imzalı olmalı; öğrenci ve danışman onay kısımları boş kalmalı."""

    code = "signatures"
    description = "İşveren kaşe/imzası ile onay kısımlarının durumu"

    def validate(self, data: Ek16Data, context: ValidationContext) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        if not data.has_company_stamp:
            issues.append(self._issue("has_company_stamp", "Belgede firma kaşesi ve yetkili imzası bulunamadı."))
        if data.has_student_signature or data.student_approval_date or "student_approval_date" in data.unparsed:
            issues.append(self._issue("has_student_signature", "Öğrenci onay kısmı boş bırakılmalı."))
        if data.has_advisor_entry:
            issues.append(self._issue("has_advisor_entry", "Staj danışmanı onay kısmı boş bırakılmalı."))
        return issues
