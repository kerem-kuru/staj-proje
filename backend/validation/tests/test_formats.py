from dataclasses import replace

import pytest

from validation.types import Severity
from validation.validators import (
    AddressFormatValidator,
    EmailFormatValidator,
    ForeignIdValidator,
    NationalIdValidator,
    PhoneFormatValidator,
    TurkishIdValidator,
)


class TestTurkishIdValidator:
    @pytest.mark.parametrize("value", ["10000000146", "12345678950"])
    def test_valid_numbers(self, value):
        assert TurkishIdValidator().is_valid_value(value)

    @pytest.mark.parametrize(
        "value",
        ["12345678901", "01234567890", "1234567895", "1234567895a", "123456789500"],
        ids=["yanlis-kontrol-basamagi", "sifirla-baslar", "10-hane", "harf", "12-hane"],
    )
    def test_invalid_numbers(self, value):
        assert not TurkishIdValidator().is_valid_value(value)


class TestForeignIdValidator:
    def test_valid_number(self):
        assert ForeignIdValidator().is_valid_value("99123456780")

    @pytest.mark.parametrize("value", ["12345678950", "9912345678", "991234567801", "9912345678a"])
    def test_invalid_numbers(self, value):
        assert not ForeignIdValidator().is_valid_value(value)


class TestNationalIdValidator:
    """Uyruğa göre doğru kuralın seçildiğini denetler."""

    def test_turkish_citizen_uses_algorithm(self, valid_data, context):
        valid_data.national_id = "12345678901"
        [issue] = NationalIdValidator().validate(valid_data, context)
        assert issue.field == "national_id"
        assert issue.message == "Belgedeki numara geçerli bir T.C. kimlik numarası değil."

    def test_foreign_student_needs_99_prefix(self, valid_data, context):
        valid_data.nationality = "Azerbaycan"
        valid_data.national_id = "12345678950"  # T.C. algoritmasından geçer ama 99 ile başlamaz
        [issue] = NationalIdValidator().validate(valid_data, context)
        assert issue.message == "Yabancı uyruklu öğrencinin kimlik numarası 11 haneli olmalı ve 99 ile başlamalı."

    def test_foreign_student_with_valid_number(self, valid_data, context):
        valid_data.nationality = "Azerbaycan"
        valid_data.national_id = "99123456780"
        assert NationalIdValidator().validate(valid_data, context) == []

    def test_dataset_nationality_is_used_when_form_has_none(self, valid_data, context):
        context.student.nationality = "Suriye"
        valid_data.nationality = None
        valid_data.national_id = "10000000146"
        assert len(NationalIdValidator().validate(valid_data, context)) == 1

    @pytest.mark.parametrize("value", ["T.C.", "TC", "t.c", "Türkiye", "TÜRK", "Türkiye Cumhuriyeti"])
    def test_turkish_spellings(self, valid_data, context, value):
        valid_data.nationality = value
        assert NationalIdValidator().validate(valid_data, context) == []

    def test_empty_value_is_left_to_required_fields(self, valid_data, context):
        valid_data.national_id = None
        assert NationalIdValidator().validate(valid_data, context) == []

    def test_no_student_record(self, valid_data, context):
        valid_data.nationality = None
        assert NationalIdValidator().validate(valid_data, replace(context, student=None)) == []


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
    def test_valid(self):
        assert PhoneFormatValidator("student_phone").is_valid_value("+90 555 123 45 67")

    @pytest.mark.parametrize(
        "value",
        ["0555 123 45 67", "05551234567", "+905551234567", "+90 555 1234567", "+90 555 123 45 6", "12"],
    )
    def test_invalid(self, value):
        assert not PhoneFormatValidator("student_phone").is_valid_value(value)

    def test_reports_expected_format(self, valid_data, context):
        valid_data.company_phone = "12"
        [issue] = PhoneFormatValidator("company_phone").validate(valid_data, context)
        assert issue.field == "company_phone"
        assert issue.message == "'Staj yeri telefon no' +90 xxx xxx xx xx biçiminde olmalı."

    def test_empty_fax_is_allowed(self, valid_data, context):
        valid_data.company_fax = None
        assert PhoneFormatValidator("company_fax").validate(valid_data, context) == []


class TestAddressFormatValidator:
    @pytest.mark.parametrize(
        "value",
        [
            "Umuttepe Mah., Yıldız Sok., No: 12, Daire: 3, İzmit/Kocaeli",
            "UMUTTEPE MAHALLESİ ATATÜRK CADDESİ NO:12 DAİRE NO:3 İZMİT / KOCAELİ",
            "Umuttepe Mah. Yıldız Sk. Bina No: 12 D: 3 İzmit/Kocaeli",
        ],
    )
    def test_valid(self, value):
        assert AddressFormatValidator("home_address").is_valid_value(value)

    @pytest.mark.parametrize(
        "value",
        [
            "Yıldız Sok., No: 12, Daire: 3, İzmit/Kocaeli",
            "Umuttepe Mah., No: 12, Daire: 3, İzmit/Kocaeli",
            "Umuttepe Mah., Yıldız Sok., Daire: 3, İzmit/Kocaeli",
            "Umuttepe Mah., Yıldız Sok., No: 12, İzmit/Kocaeli",
            "Umuttepe Mah., Yıldız Sok., No: 12, Daire: 3",
            "Yıldız Sok., Umuttepe Mah., No: 12, Daire: 3, İzmit/Kocaeli",
        ],
        ids=["mahalle-yok", "sokak-yok", "bina-yok", "daire-yok", "ilce-il-yok", "sira-yanlis"],
    )
    def test_invalid(self, value):
        assert not AddressFormatValidator("home_address").is_valid_value(value)

    def test_can_be_a_warning(self, valid_data, context):
        valid_data.company_address = "Kocaeli Teknopark"
        [issue] = AddressFormatValidator("company_address", Severity.WARNING).validate(valid_data, context)
        assert issue.severity is Severity.WARNING
