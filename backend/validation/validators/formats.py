import re

from .base import FieldFormatValidator

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class NationalIdValidator(FieldFormatValidator):
    """T.C. kimlik numarasını resmî kontrol basamağı algoritmasıyla denetler.

    Formdaki alan 'T.C. kimlik no / uyruğu' olduğundan yabancı uyruklu öğrencinin
    yazdığı uyruk (yalnızca harf, ör. 'Azerbaycan') kabul edilir.
    """

    code = "national_id_format"
    description = "T.C. kimlik numarasının geçerli olması"

    def __init__(self, field_name: str = "national_id") -> None:
        super().__init__(field_name)

    def is_valid_value(self, value: str) -> bool:
        value = value.strip()
        if re.fullmatch(r"[^\W\d_]+(?:[\s-][^\W\d_]+)*", value):
            return True  # uyruk
        if len(value) != 11 or not value.isdigit() or value[0] == "0":
            return False
        d = [int(ch) for ch in value]
        tenth = ((d[0] + d[2] + d[4] + d[6] + d[8]) * 7 - (d[1] + d[3] + d[5] + d[7])) % 10
        eleventh = sum(d[:10]) % 10
        return d[9] == tenth and d[10] == eleventh

    def error_message(self, label: str) -> str:
        return f"'{label}' geçerli bir T.C. kimlik numarası değil."


class EmailFormatValidator(FieldFormatValidator):
    code = "email_format"
    description = "E-posta adreslerinin biçimi"

    def is_valid_value(self, value: str) -> bool:
        return bool(_EMAIL_RE.match(value.strip()))

    def error_message(self, label: str) -> str:
        return f"'{label}' geçerli bir e-posta adresi değil."


class PhoneFormatValidator(FieldFormatValidator):
    """Türkiye telefon numarası: başındaki +90 / 0 atıldıktan sonra 10 hane."""

    code = "phone_format"
    description = "Telefon numaralarının biçimi"

    def is_valid_value(self, value: str) -> bool:
        digits = re.sub(r"[\s\-().]", "", value)
        if digits.startswith("+90"):
            digits = digits[3:]
        elif digits.startswith("0"):
            digits = digits[1:]
        return len(digits) == 10 and digits.isdigit() and digits[0] != "0"

    def error_message(self, label: str) -> str:
        return f"'{label}' geçerli bir telefon numarası değil."
