from readers.ek16 import Ek16Data

from ..context import ValidationContext
from ..types import Severity, ValidationIssue
from .base import BaseValidator

MIN_ENGINEERS = 1
ASK_DEPARTMENT_BELOW = 5


class EngineerCountValidator(BaseValidator):
    code = "engineer_count"
    description = "Staj yerinde yeterli mühendis bulunması"

    def validate(self, data: Ek16Data, context: ValidationContext) -> list[ValidationIssue]:
        count = data.engineer_count
        if count is None:
            return []
        if count < MIN_ENGINEERS:
            return [self._issue("engineer_count", "Staj yerinde en az 1 mühendis bulunmalı.")]
        if count < ASK_DEPARTMENT_BELOW:
            return [
                self._issue(
                    "engineer_count",
                    "Mühendis sayısı 5'in altında; mühendisin mezun olduğu bölümü belirtin.",
                    Severity.WARNING,
                )
            ]
        return []
