"""Öğrenci veri setinin içe aktarılması.

`StudentDatasetImporter` satırları okuyup kaydetmeyi yönetir; dosya biçimine
özgü ayrıştırma alt sınıflara bırakılır (soyutlama). Excel desteği gerekirse
yalnızca yeni bir alt sınıf eklenir.
"""
import csv
import io
from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import IO, ClassVar

from django.db import transaction

from .models import StudentProfile


@dataclass
class ImportResult:
    created: int = 0
    updated: int = 0
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {"created": self.created, "updated": self.updated, "errors": self.errors}


class StudentDatasetImporter(ABC):
    # Veri setindeki sütun adı -> StudentProfile alanı
    COLUMNS: ClassVar[dict[str, str]] = {
        "ogrenci_no": "student_number",
        "ad": "first_name",
        "soyad": "last_name",
        "tc_kimlik_no": "national_id",
        "bolum": "department",
        "sinif": "class_year",
        "eposta": "email",
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
            values = self._to_profile_values(row)
            if values is None:
                result.errors.append(f"{line_no}. satır: 'sinif' sayı olmalı.")
                continue
            number = values.pop("student_number")
            _, created = StudentProfile.objects.update_or_create(student_number=number, defaults=values)
            if created:
                result.created += 1
            else:
                result.updated += 1
        return result

    def _to_profile_values(self, row: dict[str, str]) -> dict[str, object] | None:
        values: dict[str, object] = {}
        for column, field_name in self.COLUMNS.items():
            values[field_name] = (row.get(column) or "").strip()
        class_year = values["class_year"]
        if class_year:
            if not str(class_year).isdigit():
                return None
            values["class_year"] = int(str(class_year))
        else:
            values["class_year"] = None
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
