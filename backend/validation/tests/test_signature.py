from validation.validators import SignatureValidator


def test_signed_document_passes(valid_data, context):
    assert SignatureValidator().validate(valid_data, context) == []


def test_missing_signatures_are_reported(valid_data, context):
    valid_data.has_student_signature = False
    valid_data.has_company_stamp = False

    issues = SignatureValidator().validate(valid_data, context)

    assert [i.field for i in issues] == ["has_student_signature", "has_company_stamp"]
