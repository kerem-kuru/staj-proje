from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from accounts.models import Role, User
from accounts.services import register_student
from students.services import CsvStudentImporter

SAMPLE_CSV = Path(settings.BASE_DIR) / "students" / "fixtures" / "ornek_ogrenciler.csv"

ADMIN_EMAIL, ADMIN_PASSWORD = "admin@staj.local", "Admin.12345"
STUDENT_EMAIL, STUDENT_PASSWORD = "ayse@ogrenci.edu.tr", "Ogrenci.12345"


class Command(BaseCommand):
    help = "Geliştirme için örnek öğrenci veri seti, bir admin ve bir öğrenci hesabı oluşturur."

    def handle(self, *args: Any, **options: Any) -> None:
        if not settings.DEBUG:
            raise CommandError("Bu komut yalnızca DEBUG açıkken çalışır.")

        with SAMPLE_CSV.open("rb") as stream:
            result = CsvStudentImporter().import_stream(stream)
        self.stdout.write(f"Veri seti: {result.created} eklendi, {result.updated} güncellendi.")

        if not User.objects.filter(email=ADMIN_EMAIL).exists():
            User.objects.create_superuser(
                email=ADMIN_EMAIL, password=ADMIN_PASSWORD, first_name="Staj", last_name="Yöneticisi"
            )
        if not User.objects.filter(email=STUDENT_EMAIL).exists():
            register_student(
                email=STUDENT_EMAIL,
                password=STUDENT_PASSWORD,
                first_name="Ayşe",
                last_name="Yılmaz",
                student_number="220101001",
            )

        self.stdout.write(self.style.SUCCESS("Demo hesapları hazır:"))
        self.stdout.write(f"  {Role.ADMIN.label}: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        self.stdout.write(f"  {Role.STUDENT.label}: {STUDENT_EMAIL} / {STUDENT_PASSWORD}")
