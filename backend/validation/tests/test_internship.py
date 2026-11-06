from dataclasses import replace
from datetime import date

from documents.services.internship_plan import HolidayCalendar, InternshipPlan
from validation.types import Severity
from validation.validators import InternshipDatesValidator, WorkDaysValidator


class TestInternshipDatesValidator:
    def test_valid_dates(self, valid_data, context):
        assert InternshipDatesValidator().validate(valid_data, context) == []

    def test_end_before_start(self, valid_data, context):
        valid_data.end_date = date(2027, 6, 10)
        issues = InternshipDatesValidator().validate(valid_data, context)
        assert [i.field for i in issues] == ["end_date"]

    def test_start_in_past(self, valid_data, context):
        valid_data.start_date = date(2027, 4, 26)
        issues = InternshipDatesValidator().validate(valid_data, context)
        assert [i.message for i in issues] == ["Staj başlama tarihi geçmiş bir tarih olamaz."]

    def test_form_must_be_submitted_30_days_before_start(self, valid_data, context):
        valid_data.start_date = date(2027, 5, 17)  # 14 gün sonra
        [issue] = InternshipDatesValidator().validate(valid_data, context)
        assert issue.severity is Severity.ERROR
        assert issue.message == (
            "Staj kabul formu staj başlama tarihinden en az 30 gün önce teslim edilmelidir; "
            "stajın başlamasına 14 gün kaldı. Önerilen teslim tarihi en geç 17.04.2027; bugün teslim için "
            "staj en erken 02.06.2027 tarihinde başlamalı."
        )

    def test_exactly_30_days_is_enough(self, valid_data, context):
        valid_data.start_date = date(2027, 6, 2)
        assert InternshipDatesValidator().validate(valid_data, context) == []

    def test_weekend_start_is_warning(self, valid_data, context):
        valid_data.start_date = date(2027, 6, 12)  # cumartesi
        [issue] = InternshipDatesValidator().validate(valid_data, context)
        assert issue.severity is Severity.WARNING

    def test_missing_dates_are_skipped(self, valid_data, context):
        valid_data.start_date = None
        assert InternshipDatesValidator().validate(valid_data, context) == []


class TestWorkDaysValidator:
    def test_declared_matches_plan(self, valid_data, context):
        assert WorkDaysValidator().validate(valid_data, context) == []

    def test_declared_does_not_match(self, valid_data, context):
        valid_data.work_days = 25
        [issue] = WorkDaysValidator().validate(valid_data, context)
        assert issue.message == "Formda staj gün sayısı 25 yazıyor, ancak seçtiğiniz plana göre 20 iş günü var."

    def test_document_dates_must_match_selected_dates(self, valid_data, context):
        valid_data.start_date = date(2027, 6, 21)
        valid_data.end_date = date(2027, 7, 16)
        issues = WorkDaysValidator().validate(valid_data, context)
        assert [i.field for i in issues] == ["start_date", "end_date"]
        assert issues[0].message == "Belgedeki 'Staj başlama tarihi' seçtiğiniz tarihle (14.06.2027) uyuşmuyor."

    def test_selected_weekdays_change_the_count(self, valid_data, context):
        plan = InternshipPlan(date(2027, 6, 14), date(2027, 7, 9), frozenset({0, 1, 2}))
        issues = WorkDaysValidator().validate(valid_data, replace(context, selected_plan=plan))
        assert "en az 20 iş günü" in issues[0].message  # haftada 3 günden 12 gün
        assert "12 iş günü var" in issues[1].message

    def test_official_holidays_are_not_counted(self, valid_data, context):
        calendar = HolidayCalendar([date(2027, 6, 15)])
        plan = InternshipPlan(date(2027, 6, 14), date(2027, 7, 9), calendar=calendar)
        issues = WorkDaysValidator().validate(valid_data, replace(context, selected_plan=plan))
        assert len(issues) == 2  # 19 iş günü: hem yetersiz hem uyuşmuyor

    def test_weekend_in_plan_but_not_in_form(self, valid_data, context):
        plan = InternshipPlan.from_work_days(date(2027, 6, 14), 20, frozenset(range(6)))
        valid_data.end_date, valid_data.work_days = plan.end_date, plan.work_days
        [issue] = WorkDaysValidator().validate(valid_data, replace(context, selected_plan=plan))
        assert issue.field == "works_weekend"
