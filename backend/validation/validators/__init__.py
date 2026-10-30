from .base import BaseValidator, FieldFormatValidator
from .declarations import HealthStatusValidator, InternshipConditionsValidator
from .formats import EmailFormatValidator, NationalIdValidator, PhoneFormatValidator
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
        InternshipDatesValidator(),
        WorkDaysValidator(),
        HealthStatusValidator(),
        InternshipConditionsValidator(),
        SignatureValidator(),
    ]


__all__ = [
    "BaseValidator",
    "EmailFormatValidator",
    "FieldFormatValidator",
    "HealthStatusValidator",
    "InternshipConditionsValidator",
    "InternshipDatesValidator",
    "NationalIdValidator",
    "PhoneFormatValidator",
    "RequiredFieldsValidator",
    "SignatureValidator",
    "StudentIdentityValidator",
    "UnparsedValuesValidator",
    "WorkDaysValidator",
    "default_validators",
]
