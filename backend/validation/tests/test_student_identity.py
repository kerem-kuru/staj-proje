from dataclasses import replace

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


def test_department_difference_is_only_a_warning(valid_data, context):
    valid_data.department = "Bilgisayar Müh."
    [issue] = StudentIdentityValidator().validate(valid_data, context)
    assert issue.severity is Severity.WARNING


def test_missing_student_record(valid_data, context):
    [issue] = StudentIdentityValidator().validate(valid_data, replace(context, student=None))
    assert issue.message == "Belge sahibi öğrenci veri setinde bulunamadı."
