import re

from readers.ek16 import Ek16Data
from readers.parsing import is_turkish_nationality, normalize_tr

from ..context import ValidationContext
from ..types import ValidationIssue
from .base import BaseValidator, FieldFormatValidator

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE_RE = re.compile(r"^\+90 \d{3} \d{3} \d{2} \d{2}$")
# Adresin bölümleri, aranacakları sırayla (metin normalize_tr ile küçültülmüş olur).
_ADDRESS_PARTS = tuple(
    re.compile(pattern)
    for pattern in (
        r"\b(mahallesi|mahalle|mah)\b",
        r"\b(caddesi|cadde|cad|cd|sokağı|sokak|sok|sk|bulvarı|bulvar|blv)\b",
        r"\b(?<!daire )(bina no|no)\s*[:.]?\s*\d+",
        r"\b(daire no|daire|d)\s*[:.]?\s*\d+",
        r"[^\W\d_]+\s*/\s*[^\W\d_]+\.?\s*$",
    )
)


class TurkishIdValidator(FieldFormatValidator):
    """T.C. kimlik numarasını resmî kontrol basamağı algoritmasıyla denetler."""

    code = "national_id_format"
    description = "T.C. kimlik numarasının geçerli olması"

    def __init__(self, field_name: str = "national_id") -> None:
        super().__init__(field_name)

    def is_valid_value(self, value: str) -> bool:
        value = value.strip()
        if len(value) != 11 or not value.isdigit() or value[0] == "0":
            return False
        d = [int(ch) for ch in value]
        tenth = ((d[0] + d[2] + d[4] + d[6] + d[8]) * 7 - (d[1] + d[3] + d[5] + d[7])) % 10
        eleventh = sum(d[:10]) % 10
        return d[9] == tenth and d[10] == eleventh

    def error_message(self, label: str) -> str:
        return "Belgedeki numara geçerli bir T.C. kimlik numarası değil."


class ForeignIdValidator(FieldFormatValidator):
    """Yabancı uyruklu öğrenci: 11 hane ve 99 ile başlar."""

    code = "national_id_format"
    description = "Yabancı kimlik numarasının geçerli olması"

    def __init__(self, field_name: str = "national_id") -> None:
        super().__init__(field_name)

    def is_valid_value(self, value: str) -> bool:
        value = value.strip()
        return len(value) == 11 and value.isdigit() and value.startswith("99")

    def error_message(self, label: str) -> str:
        return "Yabancı uyruklu öğrencinin kimlik numarası 11 haneli olmalı ve 99 ile başlamalı."


class NationalIdValidator(BaseValidator):
    """Uyruğa göre uygun kimlik kuralını seçer; belgede uyruk yoksa veri setindeki uyruk kullanılır."""

    code = "national_id_format"
    description = "Kimlik numarasının uyruğa uygun olması"

    def __init__(self) -> None:
        self._turkish = TurkishIdValidator()
        self._foreign = ForeignIdValidator()

    def validate(self, data: Ek16Data, context: ValidationContext) -> list[ValidationIssue]:
        nationality = data.nationality or (context.student.nationality if context.student else None)
        rule = self._turkish if is_turkish_nationality(nationality) else self._foreign
        return rule.validate(data, context)


class EmailFormatValidator(FieldFormatValidator):
    code = "email_format"
    description = "E-posta adreslerinin biçimi"

    def is_valid_value(self, value: str) -> bool:
        return bool(_EMAIL_RE.match(value.strip()))

    def error_message(self, label: str) -> str:
        return f"'{label}' geçerli bir e-posta adresi değil."


class PhoneFormatValidator(FieldFormatValidator):
    code = "phone_format"
    description = "Telefon numaralarının +90 xxx xxx xx xx biçiminde olması"

    def is_valid_value(self, value: str) -> bool:
        return bool(_PHONE_RE.match(value.strip()))

    def error_message(self, label: str) -> str:
        return f"'{label}' +90 xxx xxx xx xx biçiminde olmalı."


class AddressFormatValidator(FieldFormatValidator):
    code = "address_format"
    description = "Adresin Mahalle, Cadde/Sokak, Bina No, Daire No, İlçe/İl sırasıyla ve tam olması"

    def is_valid_value(self, value: str) -> bool:
        text = normalize_tr(value)
        position = 0
        for part in _ADDRESS_PARTS:
            match = part.search(text, position)
            if match is None:
                return False
            position = match.end()
        return True

    def error_message(self, label: str) -> str:
        return (
            f"'{label}' Mahalle, Cadde/Sokak, Bina No, Daire No, İlçe/İl sırasıyla ve tam yazılmalı "
            "(ör. Umuttepe Mah., Yıldız Sok., No: 12, Daire: 3, İzmit/Kocaeli)."
        )
