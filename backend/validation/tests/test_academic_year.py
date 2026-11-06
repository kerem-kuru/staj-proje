from dataclasses import replace
from datetime import date

import pytest

from validation.validators import AcademicYearValidator


def test_valid_year_and_semester(valid_data, context):
    assert AcademicYearValidator().validate(valid_data, context) == []


@pytest.mark.parametrize("semester", ["Güz", "BAHAR", "yaz"])
def test_semesters(valid_data, context, semester):
    valid_data.academic_year = f"2026-2027 {semester}"
    assert AcademicYearValidator().validate(valid_data, context) == []


@pytest.mark.parametrize("value", ["2026-2027", "2026 Güz", "Güz", "2026-2027 Kış"])
def test_year_and_semester_are_required(valid_data, context, value):
    valid_data.academic_year = value
    [issue] = AcademicYearValidator().validate(valid_data, context)
    assert issue.message == "Öğretim yılı yarıyıl bilgisiyle birlikte yazılmalı (ör. 2026-2027 Güz)."


def test_years_must_be_consecutive(valid_data, context):
    valid_data.academic_year = "2026-2028 Güz"
    [issue] = AcademicYearValidator().validate(valid_data, context)
    assert issue.message == "Öğretim yılındaki yıllar ardışık olmalı (ör. 2026-2027)."


def test_year_must_match_dataset(valid_data, context):
    context.student.submission_year = "2025-2026"
    [issue] = AcademicYearValidator().validate(valid_data, context)
    assert "veri setindeki teslim yılıyla (2025-2026)" in issue.message


def test_dates_must_be_inside_academic_year(valid_data, context):
    valid_data.start_date = date(2027, 10, 4)
    valid_data.end_date = date(2027, 10, 29)
    [issue] = AcademicYearValidator().validate(valid_data, context)
    assert issue.message == "Staj tarihleri 2026-2027 öğretim yılı ile uyumlu değil."


def test_empty_year_is_left_to_required_fields(valid_data, context):
    valid_data.academic_year = None
    assert AcademicYearValidator().validate(valid_data, context) == []


def test_without_student_record(valid_data, context):
    assert AcademicYearValidator().validate(valid_data, replace(context, student=None)) == []
