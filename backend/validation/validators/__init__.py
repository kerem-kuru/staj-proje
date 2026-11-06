from ..types import Severity
from .academic_year import AcademicYearValidator
from .base import BaseValidator, FieldFormatValidator
from .declarations import HealthStatusValidator, InternshipConditionsValidator
from .engineers import EngineerCountValidator
from .formats import (
    AddressFormatValidator,
    EmailFormatValidator,
    ForeignIdValidator,
    NationalIdValidator,
    PhoneFormatValidator,
    TurkishIdValidator,
)
from .internship import InternshipDatesValidator, WorkDaysValidator
from .required_fields import RequiredFieldsValidator, UnparsedValuesValidator
from .signature import SignatureValidator
from .student_identity import StudentIdentityValidator


def default_validators() -> list[BaseValidator]:
    """Ek-16 için çalıştırılacak denetleyiciler, rapordaki sırayla."""
    return [
        RequiredFieldsValidator(),
        UnparsedValuesValidator(),
        StudentIdentityValidator(),
        NationalIdValidator(),
        EmailFormatValidator("student_email"),
        EmailFormatValidator("company_email"),
        EmailFormatValidator("supervisor_email"),
        PhoneFormatValidator("student_phone"),
        PhoneFormatValidator("company_phone"),
        PhoneFormatValidator("company_fax"),
        PhoneFormatValidator("supervisor_phone"),
        AddressFormatValidator("home_address"),
        # İş yerlerinde daire no her zaman olmadığı için staj yeri adresi yalnızca uyarı verir.
        AddressFormatValidator("company_address", Severity.WARNING),
        AcademicYearValidator(),
        InternshipDatesValidator(),
        WorkDaysValidator(),
        EngineerCountValidator(),
        HealthStatusValidator(),
        InternshipConditionsValidator(),
        SignatureValidator(),
    ]


__all__ = [
    "AcademicYearValidator",
    "AddressFormatValidator",
    "BaseValidator",
    "EmailFormatValidator",
    "EngineerCountValidator",
    "FieldFormatValidator",
    "ForeignIdValidator",
    "HealthStatusValidator",
    "InternshipConditionsValidator",
    "InternshipDatesValidator",
    "NationalIdValidator",
    "PhoneFormatValidator",
    "RequiredFieldsValidator",
    "SignatureValidator",
    "StudentIdentityValidator",
    "TurkishIdValidator",
    "UnparsedValuesValidator",
    "WorkDaysValidator",
    "default_validators",
]
