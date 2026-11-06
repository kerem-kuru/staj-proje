"""Ek-16 (Kocaeli Üniversitesi Mühendislik Fakültesi Staj Kabul Formu) bilgilerinin tipli gösterimi.

Okuyucular (PDF, Mock, ileride Gemini) bu yapıyı üretir; denetleyiciler bu yapıyı tüketir.
Böylece denetim kuralları belgenin nasıl okunduğundan bağımsızdır.
Alanlar formdaki sırayla tanımlanmıştır; etiketler formdaki adlardır.
"""
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field, fields
from datetime import date
from typing import Any

from .parsing import clean, parse_choice, parse_date, parse_int, parse_text, parse_yes_no

DATE_FIELDS = ("birth_date", "start_date", "end_date", "student_approval_date")
HEALTH_STATUS_OPTIONS = range(1, 7)
NO_SOCIAL_SECURITY = 6  # "Herhangi bir sosyal güvencem olmadığından sağlık yardımı alamıyorum"


def _field(label: str, kind: str = "text", default: Any = None) -> Any:
    return field(default=default, metadata={"label": label, "kind": kind})


@dataclass
class Ek16Data:
    # ÖĞRENCİNİN
    national_id: str | None = _field("T.C. kimlik no / yabancı kimlik no")
    nationality: str | None = _field("Uyruğu")
    department: str | None = _field("Bölümü")
    student_full_name: str | None = _field("Öğrenci adı soyadı")
    previous_internship_days: int | None = _field("Daha önce yaptığı staj gün sayısı", "int")
    birth_date: date | None = _field("Doğum tarihi", "date")
    academic_year: str | None = _field("Öğretim yılı")
    student_number: str | None = _field("Öğrenci numarası")
    student_email: str | None = _field("Öğrenci e-posta adresi")
    student_phone: str | None = _field("Öğrenci telefon no")
    home_address: str | None = _field("İkametgâh adresi")
    health_status: int | None = _field("Sağlık yardım statüsü", "choice")
    # STAJ YAPILAN YERİN
    company_name: str | None = _field("Staj yeri adı")
    is_abroad: bool | None = _field("Yurtdışı stajı mı (E/H)", "yes_no")
    service_area: str | None = _field("Hizmet alanı")
    start_date: date | None = _field("Staj başlama tarihi", "date")
    company_phone: str | None = _field("Staj yeri telefon no")
    end_date: date | None = _field("Staj bitiş tarihi", "date")
    company_fax: str | None = _field("Staj yeri faks no")
    work_days: int | None = _field("Staj gün sayısı", "int")
    company_email: str | None = _field("Staj yeri e-posta adresi")
    works_weekend: bool | None = _field("Hafta sonu çalışılıyor mu (E/H)", "yes_no")
    company_website: str | None = _field("Staj yeri web adresi")
    employee_count: int | None = _field("Çalışan sayısı", "int")
    engineer_count: int | None = _field("Mühendis sayısı", "int")
    is_paid: bool | None = _field("Ücret alıyor mu (E/H)", "yes_no")
    company_address: str | None = _field("Staj yeri adres bilgisi")
    # İŞVEREN VEYA YETKİLİNİN
    supervisor_name: str | None = _field("Yetkili adı soyadı")
    supervisor_title: str | None = _field("Yetkili görev / unvanı")
    supervisor_email: str | None = _field("Yetkili e-posta adresi")
    supervisor_phone: str | None = _field("Yetkili telefon no")
    has_company_stamp: bool = _field("İşveren imza / kaşe", "flag", False)
    # ÖĞRENCİNİN ONAYI
    student_approval_date: date | None = _field("Öğrenci onay tarihi", "date")
    has_student_signature: bool = _field("Öğrenci imzası", "flag", False)
    # STAJ DANIŞMANI ONAYI
    has_advisor_entry: bool = _field("Staj danışmanı onay kısmı dolu", "flag", False)
    # Okunan ama anlaşılamayan değerler: alan adı -> formdaki ham metin
    unparsed: dict[str, str] = field(default_factory=dict, metadata={"label": "Anlaşılamayan değerler", "kind": "meta"})

    @classmethod
    def label_for(cls, field_name: str) -> str:
        return str(cls._meta(field_name)["label"])

    @classmethod
    def kind_for(cls, field_name: str) -> str:
        return str(cls._meta(field_name)["kind"])

    @classmethod
    def _meta(cls, field_name: str) -> Any:
        for f in fields(cls):
            if f.name == field_name:
                return f.metadata
        raise KeyError(field_name)

    def labeled_items(self) -> Iterator[tuple[str, str, Any]]:
        """(alan, etiket, değer) üçlüleri; arayüzde gösterim için."""
        for f in fields(self):
            if f.metadata["kind"] != "meta":
                yield f.name, str(f.metadata["label"]), getattr(self, f.name)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {}
        for f in fields(self):
            value = getattr(self, f.name)
            data[f.name] = value.isoformat() if isinstance(value, date) else value
        return data

    @classmethod
    def from_raw(cls, raw: dict[str, str]) -> "Ek16Data":
        """Formdan okunan ham metinleri alan türüne göre çevirir.

        Çevrilemeyen değer `unparsed` içine yazılır; denetimde ayrıca raporlanır.
        """
        parsers: dict[str, Callable[[str], Any]] = {
            "text": parse_text,
            "int": parse_int,
            "date": parse_date,
            "yes_no": parse_yes_no,
            "choice": lambda text: parse_choice(text, HEALTH_STATUS_OPTIONS),
        }
        data = cls()
        for field_name, text in raw.items():
            try:
                setattr(data, field_name, parsers[cls.kind_for(field_name)](text))
            except ValueError:
                data.unparsed[field_name] = clean(text)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Ek16Data":
        known = {f.name for f in fields(cls)}
        values = {key: value for key, value in data.items() if key in known}
        for key in DATE_FIELDS:
            if isinstance(values.get(key), str):
                values[key] = date.fromisoformat(values[key])
        return cls(**values)
