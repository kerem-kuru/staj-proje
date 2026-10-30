"""Staj planı: başlangıç/bitiş tarihleri arasındaki iş günü hesabı."""
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date, timedelta

from django.conf import settings

# Her yıl aynı güne denk gelen resmî tatiller (ay, gün).
FIXED_HOLIDAYS: frozenset[tuple[int, int]] = frozenset(
    {(1, 1), (4, 23), (5, 1), (5, 19), (7, 15), (8, 30), (10, 29)}
)


class HolidayCalendar:
    """Sabit resmî tatiller + ayarlardan gelen yıla özgü tatiller (bayramlar)."""

    def __init__(self, extra_holidays: Iterable[date] = ()) -> None:
        self._extra = frozenset(extra_holidays)

    @classmethod
    def from_settings(cls) -> "HolidayCalendar":
        return cls(settings.INTERNSHIP_RULES["EXTRA_HOLIDAYS"])

    def is_holiday(self, day: date) -> bool:
        return (day.month, day.day) in FIXED_HOLIDAYS or day in self._extra


@dataclass(frozen=True)
class InternshipPlan:
    start_date: date
    end_date: date
    works_saturday: bool = False
    calendar: HolidayCalendar = field(default_factory=HolidayCalendar, compare=False)

    def is_work_day(self, day: date) -> bool:
        last_work_weekday = 5 if self.works_saturday else 4  # 0=pazartesi
        return day.weekday() <= last_work_weekday and not self.calendar.is_holiday(day)

    @property
    def work_days(self) -> int:
        if self.end_date < self.start_date:
            return 0
        total = (self.end_date - self.start_date).days + 1
        return sum(1 for offset in range(total) if self.is_work_day(self.start_date + timedelta(days=offset)))

    @classmethod
    def from_work_days(
        cls,
        start_date: date,
        work_days: int,
        works_saturday: bool = False,
        calendar: HolidayCalendar | None = None,
    ) -> "InternshipPlan":
        """Başlangıçtan itibaren `work_days` iş günü süren planı oluşturur."""
        if work_days < 1:
            raise ValueError("İş günü sayısı en az 1 olmalı.")
        probe = cls(start_date, start_date, works_saturday, calendar or HolidayCalendar())
        day, counted = start_date, 0
        while True:
            if probe.is_work_day(day):
                counted += 1
                if counted == work_days:
                    return cls(start_date, day, works_saturday, probe.calendar)
            day += timedelta(days=1)
