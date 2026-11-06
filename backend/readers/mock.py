"""Testler için sahte okuyucu — dosyanın içeriğine BAKMAZ.

Öğrencinin veri setindeki bilgilerinden geçerli bir Ek-16 üretir; bu yüzden gerçek
kullanımda (DOCUMENT_READER) seçilmemelidir. Staj tarihleri öğrencinin seçtiği plandan alınır.
Dosya adına göre hatalı senaryo üretebilir:
  - adında "eksik" geçen dosya  -> firma adı boş, firma kaşesi yok
  - adında "hatali" geçen dosya -> yanlış T.C. kimlik no, tarihlerle uyuşmayan gün sayısı
"""
import copy
from datetime import date, timedelta
from typing import TYPE_CHECKING

from django.conf import settings
from django.utils import timezone

from documents.services.internship_plan import HolidayCalendar, InternshipPlan

from .base import DocumentReader
from .ek16 import Ek16Data

if TYPE_CHECKING:
    from documents.models import Document


class MockDocumentReader(DocumentReader):
    name = "mock"

    def __init__(self, preset: Ek16Data | None = None, today: date | None = None) -> None:
        self._preset = preset
        self._today = today

    def _extract(self, content: bytes, document: "Document") -> Ek16Data:
        if self._preset is not None:
            return copy.deepcopy(self._preset)

        data = self._valid_sample(document)
        filename = document.original_filename.lower()
        if "eksik" in filename:
            data.company_name = None
            data.has_company_stamp = False
        if "hatali" in filename:
            data.national_id = "12345678901"
            data.work_days = 5
        return data

    def _valid_sample(self, document: "Document") -> Ek16Data:
        student = document.student
        today = self._today or timezone.localdate()
        plan = document.selected_plan(HolidayCalendar.from_settings()) or self._default_plan(today)
        first_year = plan.start_date.year if plan.start_date.month >= 9 else plan.start_date.year - 1
        return Ek16Data(
            national_id=student.national_id or None,
            nationality=student.nationality or None,
            department=student.department,
            student_full_name=student.full_name,
            previous_internship_days=student.previous_internship_days or 0,
            birth_date=student.birth_date or date(today.year - 21, 5, 10),
            academic_year=f"{first_year}-{first_year + 1} Güz",
            student_number=student.student_number,
            student_email=student.email or "ogrenci@ogrenci.edu.tr",
            student_phone=student.phone or "+90 555 123 45 67",
            home_address=student.home_address or "Umuttepe Mah., Yıldız Sok., No: 12, Daire: 3, İzmit/Kocaeli",
            health_status=student.health_status or 2,
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

    def _default_plan(self, today: date) -> InternshipPlan:
        start = today + timedelta(days=settings.INTERNSHIP_RULES["MIN_DAYS_BEFORE_START"] + 5)
        start += timedelta(days=(7 - start.weekday()) % 7)  # bir sonraki pazartesi
        return InternshipPlan.from_work_days(
            start, settings.INTERNSHIP_RULES["MIN_WORK_DAYS"], calendar=HolidayCalendar.from_settings()
        )
