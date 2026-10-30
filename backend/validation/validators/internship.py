from documents.services.internship_plan import InternshipPlan
from readers.ek16 import Ek16Data

from ..context import ValidationContext
from ..types import Severity, ValidationIssue
from .base import BaseValidator


class InternshipDatesValidator(BaseValidator):
    code = "internship_dates"
    description = "Staj tarihlerinin tutarlı ve formun zamanında teslim edilmiş olması"

    def validate(self, data: Ek16Data, context: ValidationContext) -> list[ValidationIssue]:
        if data.start_date is None or data.end_date is None:
            return []  # boşluk RequiredFieldsValidator tarafından raporlanır
        issues: list[ValidationIssue] = []
        if data.end_date < data.start_date:
            issues.append(self._issue("end_date", "Staj bitiş tarihi başlangıç tarihinden önce olamaz."))

        days_left = (data.start_date - context.today).days
        if days_left < 0:
            issues.append(self._issue("start_date", "Staj başlama tarihi geçmiş bir tarih olamaz."))
        elif days_left < context.min_days_before_start:
            # Ek-16 önemli not 1: form staj başlangıcından en az 30 gün önce teslim edilir.
            issues.append(
                self._issue(
                    "start_date",
                    f"Staj kabul formu staj başlama tarihinden en az {context.min_days_before_start} gün "
                    f"önce teslim edilmelidir; stajın başlamasına {days_left} gün kaldı.",
                )
            )
        if data.start_date.weekday() >= 5:
            issues.append(
                self._issue("start_date", "Staj başlama tarihi hafta sonuna denk geliyor.", Severity.WARNING)
            )
        return issues


class WorkDaysValidator(BaseValidator):
    """Formdaki staj gün sayısını tarihlerden hesaplananla ve asgari süreyle karşılaştırır.

    'Hafta sonu çalışılıyor mu' = E ise cumartesi iş günü sayılır (pazar sayılmaz).
    """

    code = "work_days"
    description = "Staj gün sayısının doğru ve yeterli olması"

    def validate(self, data: Ek16Data, context: ValidationContext) -> list[ValidationIssue]:
        if data.start_date is None or data.end_date is None or data.end_date < data.start_date:
            return []
        plan = InternshipPlan(data.start_date, data.end_date, bool(data.works_weekend), context.calendar)
        computed = plan.work_days
        issues: list[ValidationIssue] = []
        if computed < context.min_work_days:
            issues.append(
                self._issue(
                    "work_days",
                    f"Staj süresi en az {context.min_work_days} iş günü olmalı; "
                    f"belirtilen tarihler arasında {computed} iş günü var.",
                )
            )
        if data.work_days is not None and data.work_days != computed:
            issues.append(
                self._issue(
                    "work_days",
                    f"Formda staj gün sayısı {data.work_days} yazıyor, ancak tarihler arasında {computed} iş günü var.",
                )
            )
        return issues
