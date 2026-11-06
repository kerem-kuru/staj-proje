"""Metin katmanı olan Ek-16'yı (Word'de doldurulup PDF olarak kaydedilmiş) tablo hücrelerinden okur.

Form dört tablodan oluşur: ÖĞRENCİNİN, STAJ YAPILAN YERİN, İŞVEREN VEYA YETKİLİNİN ve
onay kutuları. Satırlar [etiket, değer, etiket, değer] hücrelerinden oluşur; okuyucu etiketi
tanıyıp yanındaki hücrenin metnini alır. İmza ve kaşe, ilgili kutudaki görsel/çizim
nesnelerinden anlaşılır.

Taranmış belgeler ve fotoğraflarda metin katmanı olmadığı için bu okuyucu onları okuyamaz.
"""
import io
import re
from typing import TYPE_CHECKING, Any

import pdfplumber
from pdfplumber.page import Page
from pdfplumber.table import Table

from .base import DocumentReader, ReaderError
from .ek16 import Ek16Data
from .parsing import normalize_tr, split_contact, split_identity

if TYPE_CHECKING:
    from documents.models import Document

Bbox = tuple[float, float, float, float]

SCAN_MESSAGE = (
    "Belgede okunabilir metin bulunamadı (taranmış belge veya fotoğraf). Şu an yalnızca "
    "bilgisayarda doldurulup PDF olarak kaydedilmiş Ek-16 okunabiliyor."
)
NOT_EK16_MESSAGE = "Yüklenen belge Ek-16 Staj Kabul Formu değil. Sistem yalnızca Ek-16 işler."
UNSUPPORTED_MESSAGE = (
    "Bu dosya türü kabul edildi ancak içeriği henüz otomatik okunamıyor (OCR entegrasyonu final aşamasında). "
    "Şimdilik bilgisayarda doldurulup PDF olarak kaydedilmiş Ek-16 denetlenebiliyor."
)
LAYOUT_MESSAGE = "Formun tablo yapısı tanınamadı. Lütfen değiştirilmemiş Ek-16 şablonunu kullanın."

# Normalize edilmiş etiket -> Ek16Data alanı ("_contact" e-posta/telefon olarak ikiye ayrılır)
STUDENT_LABELS = {
    "t.c. kimlik no/uyruğu": "national_id",
    "bölümü": "department",
    "adı soyadı": "student_full_name",
    "daha önce yaptığı staj gün sayısı": "previous_internship_days",
    "doğum tarihi": "birth_date",
    "öğretim yılı": "academic_year",
    "öğrenci numarası": "student_number",
    "e-posta adresi/telefon no": "_contact",
    "ikametgah adresi": "home_address",
    "sağlık yardım statüsü": "health_status",
}
WORKPLACE_LABELS = {
    "adı": "company_name",
    "yurtdışı stajımı": "is_abroad",
    "hizmet alanı": "service_area",
    "staj başlama tarihi": "start_date",
    "telefon no": "company_phone",
    "staj bitiş tarihi": "end_date",
    "faks no": "company_fax",
    "staj gün sayısı": "work_days",
    "e-posta adresi": "company_email",
    "hafta sonu çalışılıyor mu": "works_weekend",
    "web adresi": "company_website",
    "çalışan sayısı": "employee_count",
    "mühendis sayısı": "engineer_count",
    "ücret alıyor mu": "is_paid",
    "adres bilgisi": "company_address",
}
EMPLOYER_LABELS = {
    "adı soyadı": "supervisor_name",
    "görev/unvanı": "supervisor_title",
    "e-posta adresi": "supervisor_email",
    "telefon no": "supervisor_phone",
}
STAMP_LABEL = "imza/kaşe"


def label_key(text: str) -> str:
    """'Ücret Alıyor mu? (E / H) - (**)' -> 'ücret alıyor mu'"""
    first_line = text.split("\n")[0]
    first_line = re.sub(r"\(.*?\)", "", first_line)
    first_line = re.sub(r"\s*/\s*", "/", first_line)
    return normalize_tr(first_line).strip(" ?-:*")


class PdfFormReader(DocumentReader):
    name = "pdf"

    def _extract(self, content: bytes, document: "Document") -> Ek16Data:
        if not document.original_filename.lower().endswith(".pdf"):
            raise ReaderError(UNSUPPORTED_MESSAGE)
        try:
            pdf = pdfplumber.open(io.BytesIO(content))
        except Exception as exc:  # pdfminer bozuk dosyada farklı hata türleri fırlatabiliyor
            raise ReaderError("Belge PDF olarak açılamadı; dosya bozuk olabilir.") from exc
        with pdf:
            if not pdf.pages:
                raise ReaderError("Belgede sayfa bulunamadı.")
            return _Ek16Page(pdf.pages[0]).read()


class _Ek16Page:
    """Tek bir Ek-16 sayfasını okur. Sayfa nesnesi ve yardımcı metotlar dışarıya açık değildir."""

    SCAN_IMAGE_RATIO = 0.5  # sayfanın yarısından büyük görsel = taranmış sayfa

    def __init__(self, page: Page) -> None:
        self._page = page

    def read(self) -> Ek16Data:
        self._ensure_readable_ek16()
        sections = self._find_sections()
        raw: dict[str, str] = {}
        raw |= self._read_pairs(sections["student"], STUDENT_LABELS)
        raw |= self._read_pairs(sections["workplace"], WORKPLACE_LABELS)
        raw |= self._read_pairs(sections["employer"], EMPLOYER_LABELS)

        email, phone = split_contact(raw.pop("_contact", ""))
        raw["student_email"], raw["student_phone"] = email or "", phone or ""
        national_id, nationality = split_identity(raw.pop("national_id", ""))
        raw["national_id"], raw["nationality"] = national_id or "", nationality or ""

        approval_box, advisor_box = sections["approval"].rows[0].cells[:2]
        raw["student_approval_date"] = self._approval_date(approval_box)

        data = Ek16Data.from_raw(raw)
        data.has_company_stamp = self._has_graphics(self._stamp_region(sections["employer"]))
        data.has_student_signature = self._has_graphics(approval_box)
        data.has_advisor_entry = self._advisor_filled(advisor_box)
        return data

    # --- Belge kontrolü -------------------------------------------------------

    def _ensure_readable_ek16(self) -> None:
        text = self._page.extract_text() or ""
        if not text.strip() or self._looks_scanned():
            raise ReaderError(SCAN_MESSAGE)
        normalized = normalize_tr(text)
        if "ek-16" not in normalized.replace(" ", "") or "staj kabul formu" not in normalized:
            raise ReaderError(NOT_EK16_MESSAGE)

    def _looks_scanned(self) -> bool:
        page_area = float(self._page.width * self._page.height)
        return any(
            (img["x1"] - img["x0"]) * (img["bottom"] - img["top"]) > page_area * self.SCAN_IMAGE_RATIO
            for img in self._page.images
        )

    def _find_sections(self) -> dict[str, Table]:
        markers = {"student": "öğrenci numarası", "workplace": "staj başlama tarihi", "employer": "görev/unvanı"}
        sections: dict[str, Table] = {}
        for table in self._page.find_tables():
            keys = {label_key(self._text(cell)) for row in table.rows for cell in row.cells if cell}
            for section, marker in markers.items():
                if marker in keys:
                    sections[section] = table
            first_cell = table.rows[0].cells[0] if table.rows and table.rows[0].cells else None
            if first_cell and "belge üzerindeki bilgilerin" in normalize_tr(self._text(first_cell)):
                sections["approval"] = table
        if len(sections) != 4:
            raise ReaderError(LAYOUT_MESSAGE)
        return sections

    # --- Hücre okuma ------------------------------------------------------------

    def _read_pairs(self, table: Table, labels: dict[str, str]) -> dict[str, str]:
        values: dict[str, str] = {}
        for row in table.rows:
            cells = row.cells
            for index in range(0, len(cells), 2):
                label_cell = cells[index]
                value_cell = cells[index + 1] if index + 1 < len(cells) else None
                if label_cell is None or value_cell is None:
                    continue
                field_name = labels.get(label_key(self._text(label_cell)))
                if field_name:
                    # Onay kutularında kutunun yanına yazılan işaret ancak konuma göre aynı satıra düşer.
                    values[field_name] = self._text(value_cell, by_position=field_name == "health_status")
        if values.keys() != set(labels.values()):
            raise ReaderError(LAYOUT_MESSAGE)  # bir etiket bulunamadı: şablon değiştirilmiş
        return values

    def _approval_date(self, box: Bbox) -> str:
        """Onay kutusunda 'Tarih:' sonrasındaki değer. Yazım sırasına göre tarih 'İmza:'dan
        önce ya da sonra gelebilir; tarih biçimli ifade varsa o, yoksa kalan metin alınır."""
        text = self._text(box)
        if "Tarih" not in text:
            return ""
        tail = re.sub(r"^\s*:?", "", text.rsplit("Tarih", 1)[1])
        tail = re.sub(r"İmza\s*:?", " ", tail)
        date_like = re.search(r"\d{1,2}\s*[./-]\s*\d{1,2}\s*[./-]\s*\d{2,4}", tail)
        return date_like.group(0).replace(" ", "") if date_like else tail.strip()

    def _advisor_filled(self, box: Bbox) -> bool:
        """Kutunun sabit etiketleri dışında metin ya da çizim varsa danışman kısmı doldurulmuştur."""
        written = re.sub(r"(Adı|Soyadı|Tarih|İmza)\s*:", " ", self._text(box))
        return bool(written.strip()) or self._has_graphics(box)

    def _stamp_region(self, employer: Table) -> Bbox:
        """'İmza / Kaşe' hücresinden tablonun sağ alt köşesine kadar olan alan."""
        for row in employer.rows:
            for cell in row.cells:
                if cell and label_key(self._text(cell)) == STAMP_LABEL:
                    return (cell[0], cell[1], employer.bbox[2], employer.bbox[3])
        raise ReaderError(LAYOUT_MESSAGE)

    def _text(self, bbox: Bbox, by_position: bool = False) -> str:
        x0, top, x1, bottom = bbox
        inset = (x0 + 1, top + 1, x1 - 1, bottom - 1)
        # Word boş hücrelere bir boşluk karakteri koyar; konuma göre sıralama bu boşluğu
        # yazılan metnin içine sokar ("1 0000000146"). Varsayılan olarak PDF'teki yazım sırası kullanılır.
        return self._page.crop(inset).extract_text(use_text_flow=not by_position) or ""

    def _has_graphics(self, bbox: Bbox) -> bool:
        """Kutuda görsel (taranmış imza/kaşe) ya da serbest çizim (ıslak/dijital imza) var mı."""
        x0, top, x1, bottom = bbox

        def overlaps(obj: dict[str, Any]) -> bool:
            return obj["x0"] < x1 and obj["x1"] > x0 and obj["top"] < bottom and obj["bottom"] > top

        return any(overlaps(obj) for obj in [*self._page.images, *self._page.curves])
