from datetime import date

import pytest

from documents.services.internship_plan import HolidayCalendar, InternshipPlan


def test_counts_weekdays_only():
    plan = InternshipPlan(date(2027, 6, 14), date(2027, 6, 27))  # iki hafta
    assert plan.work_days == 10


def test_saturday_work():
    plan = InternshipPlan(date(2027, 6, 14), date(2027, 6, 27), weekdays=frozenset(range(6)))
    assert plan.work_days == 12


def test_selected_weekdays_only():
    plan = InternshipPlan(date(2027, 6, 14), date(2027, 6, 27), weekdays=frozenset({0, 1, 2}))
    assert plan.work_days == 6


def test_includes_weekend():
    assert InternshipPlan(date(2027, 6, 14), date(2027, 6, 27), weekdays=frozenset({0, 5})).includes_weekend
    assert not InternshipPlan(date(2027, 6, 14), date(2027, 6, 27)).includes_weekend


def test_fixed_official_holiday_is_skipped():
    plan = InternshipPlan(date(2027, 10, 25), date(2027, 10, 29))  # 29 Ekim cuma
    assert plan.work_days == 4


def test_extra_holidays():
    calendar = HolidayCalendar([date(2027, 6, 15)])
    plan = InternshipPlan(date(2027, 6, 14), date(2027, 6, 18), calendar=calendar)
    assert plan.work_days == 4


def test_from_work_days_finds_end_date():
    plan = InternshipPlan.from_work_days(date(2027, 6, 14), 20)
    assert plan.end_date == date(2027, 7, 9)
    assert plan.work_days == 20


def test_reversed_dates_have_zero_work_days():
    assert InternshipPlan(date(2027, 6, 18), date(2027, 6, 14)).work_days == 0


def test_from_work_days_requires_positive():
    with pytest.raises(ValueError):
        InternshipPlan.from_work_days(date(2027, 6, 14), 0)
