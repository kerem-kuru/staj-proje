from dataclasses import replace
from datetime import date

from documents.services.internship_plan import HolidayCalendar
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
            "stajın başlamasına 14 gün kaldı."
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
    def test_declared_matches_computed(self, valid_data, context):
        assert WorkDaysValidator().validate(valid_data, context) == []

    def test_declared_does_not_match(self, valid_data, context):
        valid_data.work_days = 25
        [issue] = WorkDaysValidator().validate(valid_data, context)
        assert issue.message == "Formda staj gün sayısı 25 yazıyor, ancak tarihler arasında 20 iş günü var."

    def test_too_short_internship(self, valid_data, context):
        valid_data.end_date = date(2027, 6, 18)  # 5 iş günü
        valid_data.work_days = 5
        [issue] = WorkDaysValidator().validate(valid_data, context)
        assert "en az 20 iş günü" in issue.message

    def test_holidays_are_not_counted(self, valid_data, context):
        holiday = HolidayCalendar([date(2027, 6, 15)])
        issues = WorkDaysValidator().validate(valid_data, replace(context, calendar=holiday))
        assert len(issues) == 2  # 19 iş günü: hem yetersiz hem uyuşmuyor

    def test_weekend_work_counts_saturdays(self, valid_data, context):
        valid_data.works_weekend = True  # 14 Haziran - 9 Temmuz arasında 3 cumartesi var
        issues = WorkDaysValidator().validate(valid_data, context)
        assert "23 iş günü var" in issues[0].message
