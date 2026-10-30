from readers.ek16 import Ek16Data
from validation.validators import RequiredFieldsValidator, UnparsedValuesValidator


class TestRequiredFieldsValidator:
    def test_valid_data_has_no_issues(self, valid_data, context):
        assert RequiredFieldsValidator().validate(valid_data, context) == []

    def test_missing_and_blank_fields_are_reported(self, valid_data, context):
        valid_data.company_name = None
        valid_data.supervisor_name = "   "

        issues = RequiredFieldsValidator().validate(valid_data, context)

        assert {issue.field for issue in issues} == {"company_name", "supervisor_name"}
        assert "'Staj yeri adı' alanı boş bırakılmış." in [issue.message for issue in issues]

    def test_unchecked_choice_has_its_own_message(self, valid_data, context):
        valid_data.health_status = None
        [issue] = RequiredFieldsValidator().validate(valid_data, context)
        assert issue.message == "'Sağlık yardım statüsü' için bir seçenek işaretlenmemiş."

    def test_blank_form_reports_every_required_field(self, context):
        issues = RequiredFieldsValidator().validate(Ek16Data(), context)
        assert len(issues) == len(RequiredFieldsValidator.REQUIRED)

    def test_fax_and_website_are_optional(self, valid_data, context):
        valid_data.company_fax = None
        valid_data.company_website = None
        assert RequiredFieldsValidator().validate(valid_data, context) == []

    def test_unparsed_field_is_not_reported_as_blank(self, valid_data, context):
        valid_data.start_date = None
        valid_data.unparsed["start_date"] = "32.13.2027"
        assert RequiredFieldsValidator().validate(valid_data, context) == []


class TestUnparsedValuesValidator:
    def test_nothing_unparsed(self, valid_data, context):
        assert UnparsedValuesValidator().validate(valid_data, context) == []

    def test_reports_raw_value_with_hint(self, valid_data, context):
        valid_data.unparsed = {"start_date": "32.13.2027", "is_paid": "belki"}

        messages = [i.message for i in UnparsedValuesValidator().validate(valid_data, context)]

        assert messages == [
            "'Staj başlama tarihi' alanındaki '32.13.2027' değeri anlaşılamadı; GG.AA.YYYY biçiminde yazılmalı.",
            "'Ücret alıyor mu (E/H)' alanındaki 'belki' değeri anlaşılamadı; E veya H yazılmalı.",
        ]
