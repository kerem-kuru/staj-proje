from pathlib import Path
from typing import Any

from django.core.management.base import BaseCommand, CommandError, CommandParser

from students.services import CsvStudentImporter


class Command(BaseCommand):
    help = "Öğrenci veri setini CSV dosyasından içe aktarır."

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("path", type=Path, help="CSV dosyasının yolu")

    def handle(self, *args: Any, **options: Any) -> None:
        path: Path = options["path"]
        if not path.exists():
            raise CommandError(f"Dosya bulunamadı: {path}")
        with path.open("rb") as stream:
            result = CsvStudentImporter().import_stream(stream)
        self.stdout.write(self.style.SUCCESS(f"Eklenen: {result.created}, güncellenen: {result.updated}"))
        for error in result.errors:
            self.stdout.write(self.style.WARNING(error))
