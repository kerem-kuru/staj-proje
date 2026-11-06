from dataclasses import replace
from datetime import date

from validation.types import Severity
from validation.validators import StudentIdentityValidator
from validation.validators.student_identity import normalize_tr


def test_matching_identity_passes(valid_data, context):
    assert StudentIdentityValidator().validate(valid_data, context) == []


def test_name_comparison_ignores_turkish_case_and_spaces(valid_data, context):
    valid_data.student_full_name = "  AYŞE   YILMAZ "
    assert StudentIdentityValidator().validate(valid_data, context) == []


def test_normalize_tr_handles_dotted_i():
    assert normalize_tr("İSMAİL IŞIK") == normalize_tr("ismail ışık")


def test_mismatches_are_errors(valid_data, context):
    valid_data.student_number = "999"
    valid_data.student_full_name = "Başka Biri"
    valid_data.national_id = "12345678950"

    issues = StudentIdentityValidator().validate(valid_data, context)

    assert {i.field for i in issues} == {"student_number", "student_full_name", "national_id"}
    assert all(i.severity is Severity.ERROR for i in issues)


def test_all_dataset_fields_are_compared(valid_data, context):
    valid_data.nationality = "Azerbaycan"
    valid_data.birth_date = date(2004, 5, 11)
    valid_data.home_address = "Başka Mah., Sokak Sok., No: 1, Daire: 1, Gebze/Kocaeli"
    valid_data.previous_internship_days = 20
    valid_data.student_email = "baska@ogrenci.edu.tr"
    valid_data.student_phone = "+90 555 000 00 00"
    valid_data.health_status = 1

    issues = StudentIdentityValidator().validate(valid_data, context)

    assert {i.field for i in issues} == {
        "nationality",
        "birth_date",
        "home_address",
        "previous_internship_days",
        "student_email",
        "student_phone",
        "health_status",
    }


def test_formatting_differences_are_ignored(valid_data, context):
    valid_data.home_address = "UMUTTEPE MAH YILDIZ SOK NO 12 DAİRE 3 İZMİT KOCAELİ"
    valid_data.nationality = "Türkiye"
    valid_data.student_phone = "0555 123 45 67"  # biçimi PhoneFormatValidator denetler
    assert StudentIdentityValidator().validate(valid_data, context) == []


def test_values_missing_in_dataset_are_not_compared(valid_data, context):
    context.student.phone = ""
    context.student.birth_date = None
    valid_data.student_phone = "+90 555 000 00 00"
    valid_data.birth_date = date(2000, 1, 1)
    assert StudentIdentityValidator().validate(valid_data, context) == []


def test_department_difference_is_only_a_warning(valid_data, context):
    valid_data.department = "Bilgisayar Müh."
    [issue] = StudentIdentityValidator().validate(valid_data, context)
    assert issue.severity is Severity.WARNING


def test_missing_student_record(valid_data, context):
    [issue] = StudentIdentityValidator().validate(valid_data, replace(context, student=None))
    assert issue.message == "Belge sahibi öğrenci veri setinde bulunamadı."
