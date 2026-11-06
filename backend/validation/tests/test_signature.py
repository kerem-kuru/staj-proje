from datetime import date

from validation.validators import SignatureValidator


def test_stamped_form_with_empty_approvals_passes(valid_data, context):
    assert SignatureValidator().validate(valid_data, context) == []


def test_missing_company_stamp(valid_data, context):
    valid_data.has_company_stamp = False
    [issue] = SignatureValidator().validate(valid_data, context)
    assert issue.field == "has_company_stamp"


def test_student_approval_must_be_empty(valid_data, context):
    valid_data.has_student_signature = True
    [issue] = SignatureValidator().validate(valid_data, context)
    assert issue.message == "Öğrenci onay kısmı boş bırakılmalı."


def test_student_approval_date_counts_as_filled(valid_data, context):
    valid_data.student_approval_date = date(2027, 5, 1)
    assert len(SignatureValidator().validate(valid_data, context)) == 1


def test_advisor_approval_must_be_empty(valid_data, context):
    valid_data.has_advisor_entry = True
    [issue] = SignatureValidator().validate(valid_data, context)
    assert issue.message == "Staj danışmanı onay kısmı boş bırakılmalı."
