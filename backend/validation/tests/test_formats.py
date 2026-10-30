import pytest

from validation.validators import EmailFormatValidator, NationalIdValidator, PhoneFormatValidator


class TestNationalIdValidator:
    @pytest.mark.parametrize("value", ["10000000146", "12345678950"])
    def test_valid_numbers(self, value):
        assert NationalIdValidator().is_valid_value(value)

    @pytest.mark.parametrize(
        "value",
        ["12345678901", "01234567890", "1234567895", "1234567895a", "123456789500"],
        ids=["yanlis-kontrol-basamagi", "sifirla-baslar", "10-hane", "harf", "12-hane"],
    )
    def test_invalid_numbers(self, value):
        assert not NationalIdValidator().is_valid_value(value)

    def test_reports_turkish_message(self, valid_data, context):
        valid_data.national_id = "12345678901"
        [issue] = NationalIdValidator().validate(valid_data, context)
        assert issue.field == "national_id"
        assert issue.message == "'T.C. kimlik no / uyruğu' geçerli bir T.C. kimlik numarası değil."

    @pytest.mark.parametrize("value", ["Azerbaycan", "Bosna-Hersek", "Kuzey Makedonya"])
    def test_nationality_is_accepted(self, value):
        assert NationalIdValidator().is_valid_value(value)

    def test_mixed_letters_and_digits_rejected(self):
        assert not NationalIdValidator().is_valid_value("TR1234567")

    def test_empty_value_is_left_to_required_fields(self, valid_data, context):
        valid_data.national_id = None
        assert NationalIdValidator().validate(valid_data, context) == []


class TestEmailFormatValidator:
    @pytest.mark.parametrize("value", ["ayse@ogrenci.edu.tr", "ik@firma.com"])
    def test_valid(self, value):
        assert EmailFormatValidator("student_email").is_valid_value(value)

    @pytest.mark.parametrize("value", ["ayse", "ayse@", "ayse@firma", "a yse@firma.com"])
    def test_invalid(self, value):
        assert not EmailFormatValidator("student_email").is_valid_value(value)

    def test_checks_only_its_own_field(self, valid_data, context):
        valid_data.company_email = "gecersiz"
        assert EmailFormatValidator("student_email").validate(valid_data, context) == []
        [issue] = EmailFormatValidator("company_email").validate(valid_data, context)
        assert issue.field == "company_email"


class TestPhoneFormatValidator:
    @pytest.mark.parametrize("value", ["0555 123 45 67", "+90 (312) 123-45-67", "5551234567"])
    def test_valid(self, value):
        assert PhoneFormatValidator("student_phone").is_valid_value(value)

    @pytest.mark.parametrize("value", ["123", "0555 123 45", "00555 123 45 67", "0555 abc 45 67"])
    def test_invalid(self, value):
        assert not PhoneFormatValidator("student_phone").is_valid_value(value)

    def test_reports_issue(self, valid_data, context):
        valid_data.company_phone = "12"
        [issue] = PhoneFormatValidator("company_phone").validate(valid_data, context)
        assert issue.message == "'Staj yeri telefon no' geçerli bir telefon numarası değil."
