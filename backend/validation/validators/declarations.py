"""Formun dipnotlarındaki beyanlarla ilgili kontroller."""
from datetime import date

from readers.ek16 import NO_SOCIAL_SECURITY, Ek16Data

from ..context import ValidationContext
from ..types import Severity, ValidationIssue
from .base import BaseValidator


def age_on(birth_date: date, day: date) -> int:
    return day.year - birth_date.year - ((day.month, day.day) < (birth_date.month, birth_date.day))


class HealthStatusValidator(BaseValidator):
    """(*) 'Sağlık yardım statüsü (25 yaş ve üstü olmanız durumunda 6- nolu seçenek işaretlenir)'."""

    code = "health_status"
    description = "Sağlık yardım statüsünün yaşa uygun işaretlenmesi"

    def validate(self, data: Ek16Data, context: ValidationContext) -> list[ValidationIssue]:
        if data.birth_date is None or data.health_status is None:
            return []
        if data.birth_date >= context.today:
            return [self._issue("birth_date", "Doğum tarihi bugünden sonra olamaz.")]
        age = age_on(data.birth_date, data.start_date or context.today)
        if age >= 25 and data.health_status != NO_SOCIAL_SECURITY:
            return [
                self._issue(
                    "health_status",
                    f"Staj başlangıcında {age} yaşında olacaksınız; formun notuna göre 25 yaş ve üstü "
                    "öğrenciler sağlık yardım statüsünde 6 numaralı seçeneği işaretler.",
                    Severity.WARNING,
                )
            ]
        return []


class InternshipConditionsValidator(BaseValidator):
    """Yurtdışı ve ücretli staj için formun hatırlattığı ek yükümlülükler (bilgilendirme)."""

    code = "internship_conditions"
    description = "Yurtdışı / ücretli staj yükümlülüklerinin hatırlatılması"

    def validate(self, data: Ek16Data, context: ValidationContext) -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        if data.is_abroad:
            issues.append(
                self._issue(
                    "is_abroad",
                    "Yurtdışı stajında SGK işlemlerini öğrenci kendi imkânlarıyla yaptırır.",
                    Severity.WARNING,
                )
            )
        if data.is_paid:
            issues.append(
                self._issue(
                    "is_paid",
                    "Ücretli stajda staj bitiminde EK-18 (Staj Ücretlerine İşsizlik Fonu Katkısı Bilgi Formu) "
                    "dekontla birlikte komisyona teslim edilmelidir.",
                    Severity.WARNING,
                )
            )
        return issues
