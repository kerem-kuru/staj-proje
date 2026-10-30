from dataclasses import dataclass, field
from datetime import date
from typing import TYPE_CHECKING

from django.conf import settings
from django.utils import timezone

from documents.services.internship_plan import HolidayCalendar
from students.models import StudentProfile

if TYPE_CHECKING:
    from documents.models import Document


@dataclass(frozen=True)
class ValidationContext:
    """Denetleyicilerin belge dışında ihtiyaç duyduğu bilgiler."""

    student: StudentProfile | None
    today: date
    min_work_days: int
    min_days_before_start: int = 30
    calendar: HolidayCalendar = field(default_factory=HolidayCalendar)

    @classmethod
    def for_document(cls, document: "Document") -> "ValidationContext":
        rules = settings.INTERNSHIP_RULES
        return cls(
            student=document.student,
            today=timezone.localdate(),
            min_work_days=rules["MIN_WORK_DAYS"],
            min_days_before_start=rules["MIN_DAYS_BEFORE_START"],
            calendar=HolidayCalendar.from_settings(),
        )
