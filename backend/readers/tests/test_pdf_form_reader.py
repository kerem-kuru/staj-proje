"""Gerçek Ek-16 şablonu (ek16_bos.pdf) ve ondan üretilmiş dolu örnek (ek16_dolu.pdf) ile testler."""
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest

from readers.base import ReaderError
from readers.pdf_form import NOT_EK16_MESSAGE, SCAN_MESSAGE, PdfFormReader, label_key
from validation.engine import ValidationEngine

from .pdf_builder import build_pdf

FIXTURES = Path(__file__).parent / "fixtures"


def read(content: bytes, filename: str = "ek16.pdf"):
    # Okuyucu belgeden yalnızca dosya adını kullanır; model nesnesi gerekmez.
    return PdfFormReader()._extract(content, SimpleNamespace(original_filename=filename))


@pytest.fixture(scope="module")
def blank():
    return read((FIXTURES / "ek16_bos.pdf").read_bytes())


@pytest.fixture(scope="module")
def filled():
    return read((FIXTURES / "ek16_dolu.pdf").read_bytes())


class TestBlankForm:
    def test_every_field_is_empty(self, blank):
        assert all(value in (None, False) for _, _, value in blank.labeled_items())
        assert blank.unparsed == {}

    def test_blank_form_fails_validation(self, blank, context):
        result = ValidationEngine.default().run(blank, context)
        assert not result.is_valid
        messages = [issue.message for issue in result.errors]
        assert "'Öğrenci adı soyadı' alanı boş bırakılmış." in messages
        assert "Belgede firma kaşesi ve yetkili imzası bulunamadı." in messages


class TestFilledForm:
    def test_student_section(self, filled):
        assert filled.national_id == "10000000146"
        assert filled.department == "Bilgisayar Mühendisliği"
        assert filled.student_full_name == "Ayşe Yılmaz"
        assert filled.previous_internship_days == 0
        assert filled.birth_date == date(2004, 5, 10)
        assert filled.student_number == "220101001"
        assert (filled.student_email, filled.student_phone) == ("ayse@ogrenci.edu.tr", "0555 123 45 67")
        assert filled.home_address == "Umuttepe Mah. İzmit / Kocaeli"
        assert filled.health_status == 2

    def test_workplace_section(self, filled):
        assert filled.company_name == "Örnek Yazılım A.Ş."
        assert (filled.start_date, filled.end_date, filled.work_days) == (date(2027, 6, 14), date(2027, 7, 9), 20)
        assert (filled.is_abroad, filled.works_weekend, filled.is_paid) == (False, False, False)
        assert (filled.employee_count, filled.engineer_count) == (45, 12)
        assert filled.company_fax is None

    def test_employer_section_and_signatures(self, filled):
        assert filled.supervisor_name == "Mehmet Öztürk"
        assert filled.supervisor_email == "mehmet@ornek.com.tr"
        assert filled.has_company_stamp is True
        assert filled.has_student_signature is True
        assert filled.student_approval_date == date(2027, 5, 1)

    def test_filled_form_passes_validation(self, filled, context):
        result = ValidationEngine.default().run(filled, context)
        assert result.is_valid, [issue.message for issue in result.issues]


class TestRejectedInputs:
    def test_other_document(self):
        with pytest.raises(ReaderError, match=NOT_EK16_MESSAGE):
            read(build_pdf("Transkript belgesi"))

    def test_scanned_page_without_text(self):
        with pytest.raises(ReaderError, match="taranmış"):
            read(build_pdf(full_page_image=True))

    def test_scanned_page_with_ocr_text(self):
        with pytest.raises(ReaderError, match="taranmış"):
            read(build_pdf("EK-16 STAJ KABUL FORMU", full_page_image=True))

    def test_image_file(self):
        with pytest.raises(ReaderError) as exc:
            read(b"\x89PNG\r\n\x1a\n", filename="ek16.png")
        assert str(exc.value) == SCAN_MESSAGE

    def test_corrupt_pdf(self):
        with pytest.raises(ReaderError, match="açılamadı"):
            read(b"%PDF-1.4 bozuk")


@pytest.mark.parametrize(
    ("label", "expected"),
    [
        ("Ücret Alıyor mu? (E / H) - (**)", "ücret alıyor mu"),
        ("T.C. KİMLİK NO/ UYRUĞU", "t.c. kimlik no/uyruğu"),
        ("İKAMETGÂH ADRESİ", "ikametgah adresi"),
        ("Yurtdışı Stajımı? (E/H)\n(E İse Öğrenci...)", "yurtdışı stajımı"),
    ],
)
def test_label_key(label, expected):
    assert label_key(label) == expected
