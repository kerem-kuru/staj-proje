from datetime import date
from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from accounts.models import User
from documents.services.internship_plan import HolidayCalendar, InternshipPlan
from readers.ek16 import Ek16Data
from students.models import StudentProfile
from validation.context import ValidationContext

TODAY = date(2027, 5, 3)  # pazartesi; staj başlangıcından (14 Haziran) 42 gün önce
PDF_BYTES = b"%PDF-1.4\n%test\n"


@pytest.fixture(autouse=True)
def _media_root(settings, tmp_path: Path) -> None:
    settings.MEDIA_ROOT = tmp_path / "media"
    settings.DOCUMENT_READER = "mock"


@pytest.fixture
def student_profile(db) -> StudentProfile:
    return StudentProfile.objects.create(
        student_number="220101001",
        first_name="Ayşe",
        last_name="Yılmaz",
        national_id="10000000146",
        department="Bilgisayar Mühendisliği",
        class_year=3,
        email="ayse@ogrenci.edu.tr",
        nationality="T.C.",
        birth_date=date(2004, 5, 10),
        home_address="Umuttepe Mah., Yıldız Sok., No: 12, Daire: 3, İzmit/Kocaeli",
        submission_year="2026-2027",
        previous_internship_days=0,
        phone="+90 555 123 45 67",
        health_status=2,
    )


@pytest.fixture
def student_user(student_profile: StudentProfile) -> User:
    user = User.objects.create_user(email="ayse@ogrenci.edu.tr", password="Gizli.12345", first_name="Ayşe")
    student_profile.user = user
    student_profile.save()
    return user


@pytest.fixture
def other_student_user(db) -> User:
    profile = StudentProfile.objects.create(
        student_number="220101002", first_name="İsmail", last_name="Kaya", department="Bilgisayar Mühendisliği"
    )
    user = User.objects.create_user(email="ismail@ogrenci.edu.tr", password="Gizli.12345")
    profile.user = user
    profile.save()
    return user


@pytest.fixture
def admin_user(db) -> User:
    return User.objects.create_superuser(email="admin@staj.local", password="Gizli.12345")


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def student_client(student_user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(student_user)
    return client


@pytest.fixture
def admin_client(admin_user: User) -> APIClient:
    client = APIClient()
    client.force_authenticate(admin_user)
    return client


@pytest.fixture
def pdf_file():
    def make(name: str = "ek16.pdf") -> SimpleUploadedFile:
        return SimpleUploadedFile(name, PDF_BYTES, content_type="application/pdf")

    return make


@pytest.fixture
def context(student_profile: StudentProfile) -> ValidationContext:
    return ValidationContext(
        student=student_profile,
        today=TODAY,
        min_work_days=20,
        min_days_before_start=30,
        calendar=HolidayCalendar(),
        selected_plan=InternshipPlan.from_work_days(date(2027, 6, 14), 20),
    )


@pytest.fixture
def valid_data() -> Ek16Data:
    """Fixture'daki öğrenci ve TODAY ile tüm kurallardan geçen Ek-16 verisi."""
    plan = InternshipPlan.from_work_days(date(2027, 6, 14), 20)
    return Ek16Data(
        national_id="10000000146",
        nationality="T.C.",
        department="Bilgisayar Mühendisliği",
        student_full_name="Ayşe Yılmaz",
        previous_internship_days=0,
        birth_date=date(2004, 5, 10),
        academic_year="2026-2027 Bahar",
        student_number="220101001",
        student_email="ayse@ogrenci.edu.tr",
        student_phone="+90 555 123 45 67",
        home_address="Umuttepe Mah., Yıldız Sok., No: 12, Daire: 3, İzmit/Kocaeli",
        health_status=2,
        company_name="Örnek Yazılım A.Ş.",
        is_abroad=False,
        service_area="Yazılım",
        start_date=plan.start_date,
        company_phone="+90 262 123 45 67",
        end_date=plan.end_date,
        work_days=plan.work_days,
        company_email="ik@ornek.com.tr",
        works_weekend=False,
        employee_count=45,
        engineer_count=12,
        is_paid=False,
        company_address="Yeşilova Mah., Teknopark Cad., No: 5, Daire: 1, Başiskele/Kocaeli",
        supervisor_name="Mehmet Öztürk",
        supervisor_title="Yazılım Müdürü",
        supervisor_email="mehmet@ornek.com.tr",
        supervisor_phone="+90 262 123 45 68",
        has_company_stamp=True,
    )
