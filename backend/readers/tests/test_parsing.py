from datetime import date

import pytest

from readers.ek16 import Ek16Data
from readers.parsing import (
    normalize_tr,
    parse_choice,
    parse_date,
    parse_int,
    parse_yes_no,
    split_contact,
)


class TestParseDate:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            ("14.06.2027", date(2027, 6, 14)),
            ("1/7/2027", date(2027, 7, 1)),
            ("14-06-2027", date(2027, 6, 14)),
            ("2027-06-14", date(2027, 6, 14)),
            (" 14 . 06 . 2027 ", date(2027, 6, 14)),
            ("14.06.27", date(2027, 6, 14)),
            ("10.05.98", date(1998, 5, 10)),
        ],
    )
    def test_formats(self, text, expected):
        assert parse_date(text, today=date(2026, 10, 30)) == expected

    def test_blank_is_none(self):
        assert parse_date("  ") is None

    @pytest.mark.parametrize("text", ["32.13.2027", "Haziran 2027", "14.06"])
    def test_invalid(self, text):
        with pytest.raises(ValueError):
            parse_date(text)


class TestParseInt:
    @pytest.mark.parametrize(("text", "expected"), [("20", 20), ("20 gün", 20), ("1.250", 1250), ("0", 0)])
    def test_valid(self, text, expected):
        assert parse_int(text) == expected

    @pytest.mark.parametrize("text", ["yirmi", "20-25"])
    def test_invalid(self, text):
        with pytest.raises(ValueError):
            parse_int(text)


class TestParseYesNo:
    @pytest.mark.parametrize(("text", "expected"), [("E", True), ("evet", True), ("H", False), ("HAYIR", False)])
    def test_valid(self, text, expected):
        assert parse_yes_no(text) is expected

    def test_blank_and_invalid(self):
        assert parse_yes_no("") is None
        with pytest.raises(ValueError):
            parse_yes_no("belki")


class TestParseChoice:
    EMPTY = "1-☐\n2-☐\n3-☐\n4-☐\n5-☐\n6-☐"

    def test_nothing_checked(self):
        assert parse_choice(self.EMPTY, range(1, 7)) is None

    @pytest.mark.parametrize("marked", ["2-☒", "2-☑", "2-☐ X", "2- x"])
    def test_one_checked(self, marked):
        assert parse_choice(self.EMPTY.replace("2-☐", marked), range(1, 7)) == 2

    def test_two_checked_is_error(self):
        with pytest.raises(ValueError):
            parse_choice(self.EMPTY.replace("1-☐", "1-☒").replace("3-☐", "3-☒"), range(1, 7))

    def test_plain_number(self):
        assert parse_choice("6", range(1, 7)) == 6


class TestSplitContact:
    def test_email_and_phone(self):
        assert split_contact("ayse@ogrenci.edu.tr / 0555 123 45 67") == ("ayse@ogrenci.edu.tr", "0555 123 45 67")

    def test_phone_first(self):
        assert split_contact("0555 123 45 67, ayse@ogrenci.edu.tr") == ("ayse@ogrenci.edu.tr", "0555 123 45 67")

    def test_only_email(self):
        assert split_contact("ayse@ogrenci.edu.tr") == ("ayse@ogrenci.edu.tr", None)


def test_normalize_tr_handles_circumflex():
    assert normalize_tr("İKAMETGÂH  ADRESİ") == "ikametgah adresi"


def test_from_raw_collects_unparsed_values():
    data = Ek16Data.from_raw({"start_date": "32.13.2027", "work_days": "20 gün", "is_paid": "H", "company_name": " A "})
    assert data.unparsed == {"start_date": "32.13.2027"}
    assert (data.work_days, data.is_paid, data.company_name) == (20, False, "A")
