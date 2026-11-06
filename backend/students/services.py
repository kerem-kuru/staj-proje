"""Öğrenci veri setinin içe aktarılması.

`StudentDatasetImporter` satırları okuyup kaydetmeyi yönetir; dosya biçimine
özgü ayrıştırma alt sınıflara bırakılır (soyutlama). Excel desteği gerekirse
yalnızca yeni bir alt sınıf eklenir.
"""
import csv
import io
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from typing import IO, Any, ClassVar

from django.db import transaction

from readers.parsing import clean, parse_date, parse_int

from .models import StudentProfile


@dataclass
class ImportResult:
    created: int = 0
    updated: int = 0
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {"created": self.created, "updated": self.updated, "errors": self.errors}


class StudentDatasetImporter(ABC):
    # Veri setindeki sütun adı -> (StudentProfile alanı, değeri çeviren fonksiyon, hata mesajındaki tür)
    COLUMNS: ClassVar[dict[str, tuple[str, Callable[[str], Any], str]]] = {
        "ogrenci_no": ("student_number", clean, "metin"),
        "ad": ("first_name", clean, "metin"),
        "soyad": ("last_name", clean, "metin"),
        "tc_kimlik_no": ("national_id", clean, "metin"),
        "uyruk": ("nationality", clean, "metin"),
        "dogum_tarihi": ("birth_date", parse_date, "GG.AA.YYYY biçiminde tarih"),
        "ikametgah_adresi": ("home_address", clean, "metin"),
        "bolum": ("department", clean, "metin"),
        "sinif": ("class_year", parse_int, "sayı"),
        "teslim_yili": ("submission_year", clean, "metin"),
        "onceki_staj_gun": ("previous_internship_days", parse_int, "sayı"),
        "eposta": ("email", clean, "metin"),
        "telefon": ("phone", clean, "metin"),
        "saglik_statusu": ("health_status", parse_int, "sayı"),
    }
    REQUIRED: ClassVar[tuple[str, ...]] = ("ogrenci_no", "ad", "soyad", "bolum")

    @abstractmethod
    def rows(self, stream: IO[bytes]) -> Iterator[dict[str, str]]:
        """Dosyadaki her satırı {sütun_adı: değer} olarak döndürür."""

    @transaction.atomic
    def import_stream(self, stream: IO[bytes]) -> ImportResult:
        result = ImportResult()
        for line_no, row in enumerate(self.rows(stream), start=2):  # 1. satır başlık
            missing = [col for col in self.REQUIRED if not row.get(col, "").strip()]
            if missing:
                result.errors.append(f"{line_no}. satır: eksik sütun(lar): {', '.join(missing)}")
                continue
            try:
                values = self._to_profile_values(row)
            except ValueError as exc:
                result.errors.append(f"{line_no}. satır: {exc}")
                continue
            number = values.pop("student_number")
            _, created = StudentProfile.objects.update_or_create(student_number=number, defaults=values)
            if created:
                result.created += 1
            else:
                result.updated += 1
        return result

    def _to_profile_values(self, row: dict[str, str]) -> dict[str, object]:
        values: dict[str, object] = {}
        for column, (field_name, parse, kind) in self.COLUMNS.items():
            try:
                values[field_name] = parse(row.get(column) or "")
            except ValueError as exc:
                raise ValueError(f"'{column}' {kind} olmalı.") from exc
        return values


class CsvStudentImporter(StudentDatasetImporter):
    """UTF-8 CSV okur; Excel'in Türkçe ayarındaki ';' ayırıcısını da tanır."""

    def rows(self, stream: IO[bytes]) -> Iterator[dict[str, str]]:
        text = stream.read().decode("utf-8-sig")
        try:
            dialect = csv.Sniffer().sniff(text.splitlines()[0], delimiters=",;")
        except (csv.Error, IndexError):
            dialect = csv.excel
        reader = csv.DictReader(io.StringIO(text), dialect=dialect)
        for row in reader:
            yield {(key or "").strip().lower(): (value or "") for key, value in row.items()}
