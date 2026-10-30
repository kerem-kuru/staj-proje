from typing import ClassVar

from readers.ek16 import Ek16Data

from ..context import ValidationContext
from ..types import ValidationIssue
from .base import BaseValidator


class RequiredFieldsValidator(BaseValidator):
    code = "required_fields"
    description = "Ek-16'daki zorunlu alanların dolu olması"

    # Faks ve web adresi her iş yerinde olmadığı için zorunlu tutulmadı.
    REQUIRED: ClassVar[tuple[str, ...]] = (
        "national_id",
        "department",
        "student_full_name",
        "previous_internship_days",
        "birth_date",
        "academic_year",
        "student_number",
        "student_email",
        "student_phone",
        "home_address",
        "health_status",
        "company_name",
        "is_abroad",
        "service_area",
        "start_date",
        "company_phone",
        "end_date",
        "work_days",
        "company_email",
        "works_weekend",
        "employee_count",
        "engineer_count",
        "is_paid",
        "company_address",
        "supervisor_name",
        "supervisor_title",
        "supervisor_email",
        "supervisor_phone",
        "student_approval_date",
    )

    def validate(self, data: Ek16Data, context: ValidationContext) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for field_name in self.REQUIRED:
            if field_name in data.unparsed:
                continue  # dolu ama anlaşılamadı; UnparsedValuesValidator raporlar
            value = getattr(data, field_name)
            if value is None or (isinstance(value, str) and not value.strip()):
                label = Ek16Data.label_for(field_name)
                message = (
                    f"'{label}' için bir seçenek işaretlenmemiş."
                    if Ek16Data.kind_for(field_name) == "choice"
                    else f"'{label}' alanı boş bırakılmış."
                )
                issues.append(self._issue(field_name, message))
        return issues


class UnparsedValuesValidator(BaseValidator):
    """Doldurulmuş ama beklenen biçimde olmayan değerleri raporlar (ör. '32.13.2027', 'belki')."""

    code = "unparsed_values"
    description = "Alanların beklenen biçimde doldurulması"

    HINTS: ClassVar[dict[str, str]] = {
        "date": "GG.AA.YYYY biçiminde yazılmalı",
        "int": "yalnızca sayı yazılmalı",
        "yes_no": "E veya H yazılmalı",
        "choice": "yalnızca bir seçenek işaretlenmeli",
    }

    def validate(self, data: Ek16Data, context: ValidationContext) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        for field_name, raw in data.unparsed.items():
            label = Ek16Data.label_for(field_name)
            hint = self.HINTS.get(Ek16Data.kind_for(field_name), "")
            message = f"'{label}' alanındaki '{raw}' değeri anlaşılamadı" + (f"; {hint}." if hint else ".")
            issues.append(self._issue(field_name, message))
        return issues
