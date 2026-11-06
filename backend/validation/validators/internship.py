from datetime import date, timedelta

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
            notice = timedelta(days=context.min_days_before_start)
            latest, earliest = data.start_date - notice, context.today + notice
            issues.append(
                self._issue(
                    "start_date",
                    f"Staj kabul formu staj başlama tarihinden en az {context.min_days_before_start} gün "
                    f"önce teslim edilmelidir; stajın başlamasına {days_left} gün kaldı. "
                    f"Önerilen teslim tarihi en geç {latest:%d.%m.%Y}; bugün teslim için staj en erken "
                    f"{earliest:%d.%m.%Y} tarihinde başlamalı.",
                )
            )
        if data.start_date.weekday() >= 5:
            issues.append(
                self._issue("start_date", "Staj başlama tarihi hafta sonuna denk geliyor.", Severity.WARNING)
            )
        return issues


class WorkDaysValidator(BaseValidator):
    """Öğrencinin seçtiği plandan hesaplanan günleri belgedeki tarih ve gün sayısıyla karşılaştırır."""

    code = "work_days"
    description = "Staj gün sayısının seçilen planla uyuşması ve yeterli olması"

    def validate(self, data: Ek16Data, context: ValidationContext) -> list[ValidationIssue]:
        plan = context.selected_plan
        if plan is None:
            return []
        computed = plan.work_days
        issues: list[ValidationIssue] = []
        if computed < context.min_work_days:
            issues.append(
                self._issue(
                    "work_days",
                    f"Staj süresi en az {context.min_work_days} iş günü olmalı; "
                    f"seçtiğiniz plana göre {computed} iş günü var.",
                )
            )
        if data.start_date is not None and data.start_date != plan.start_date:
            issues.append(self._date_mismatch("start_date", plan.start_date))
        if data.end_date is not None and data.end_date != plan.end_date:
            issues.append(self._date_mismatch("end_date", plan.end_date))
        if data.work_days is not None and data.work_days != computed:
            issues.append(
                self._issue(
                    "work_days",
                    f"Formda staj gün sayısı {data.work_days} yazıyor, ancak seçtiğiniz plana göre "
                    f"{computed} iş günü var.",
                )
            )
        if plan.includes_weekend and data.works_weekend is False:
            issues.append(
                self._issue(
                    "works_weekend", "Planda hafta sonu günü seçtiniz, ancak formda hafta sonu çalışılmıyor yazıyor."
                )
            )
        return issues

    def _date_mismatch(self, field_name: str, selected: date) -> ValidationIssue:
        label = Ek16Data.label_for(field_name)
        return self._issue(field_name, f"Belgedeki '{label}' seçtiğiniz tarihle ({selected:%d.%m.%Y}) uyuşmuyor.")
