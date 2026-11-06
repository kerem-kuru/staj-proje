"""Denetleyici hiyerarşisi.

BaseValidator (soyut)
 ├── RequiredFieldsValidator, UnparsedValuesValidator, StudentIdentityValidator,
 │   AcademicYearValidator, InternshipDatesValidator, WorkDaysValidator,
 │   EngineerCountValidator, HealthStatusValidator, InternshipConditionsValidator,
 │   SignatureValidator
 ├── NationalIdValidator (uyruğa göre aşağıdaki iki kuraldan birini çalıştırır)
 └── FieldFormatValidator (soyut, tek alanın biçimi)
      ├── TurkishIdValidator
      ├── ForeignIdValidator
      ├── EmailFormatValidator
      ├── PhoneFormatValidator
      └── AddressFormatValidator

ValidationEngine hepsini aynı `validate()` arayüzüyle çağırır (çok biçimlilik).
"""
from abc import ABC, abstractmethod
from typing import ClassVar

from readers.ek16 import Ek16Data

from ..context import ValidationContext
from ..types import Severity, ValidationIssue


class BaseValidator(ABC):
    code: ClassVar[str]
    description: ClassVar[str]

    @abstractmethod
    def validate(self, data: Ek16Data, context: ValidationContext) -> list[ValidationIssue]:
        """Belgedeki bilgileri denetler, bulunan sorunları döndürür."""

    def _issue(self, field: str | None, message: str, severity: Severity = Severity.ERROR) -> ValidationIssue:
        return ValidationIssue(code=self.code, field=field, message=message, severity=severity)


class FieldFormatValidator(BaseValidator):
    """Tek bir alanın biçimini denetler. Boş alanlar RequiredFieldsValidator'ın işidir."""

    def __init__(self, field_name: str, severity: Severity = Severity.ERROR) -> None:
        self._field_name = field_name
        self._severity = severity

    @property
    def field_name(self) -> str:
        return self._field_name

    def validate(self, data: Ek16Data, context: ValidationContext) -> list[ValidationIssue]:
        value = getattr(data, self._field_name)
        if value in (None, ""):
            return []
        if self.is_valid_value(str(value)):
            return []
        label = Ek16Data.label_for(self._field_name)
        return [self._issue(self._field_name, self.error_message(label), self._severity)]

    @abstractmethod
    def is_valid_value(self, value: str) -> bool: ...

    @abstractmethod
    def error_message(self, label: str) -> str: ...
