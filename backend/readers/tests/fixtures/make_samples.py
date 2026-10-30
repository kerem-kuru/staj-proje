"""Boş Ek-16 şablonundan (ek16_bos.pdf) testlerde kullanılan dolu örneği üretir.

Bir kez çalıştırılıp çıktı depoya eklenir; testler bu betiğe bağlı değildir.
Gereksinimler (yalnızca bu betik için): pip install reportlab pypdf
Windows'taki Arial yazı tipini kullanır (Türkçe karakterler için).

    python readers/tests/fixtures/make_samples.py
"""
import io
from pathlib import Path

import pdfplumber
from pypdf import PdfReader, PdfWriter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = Path(__file__).parent
TEMPLATE = HERE / "ek16_bos.pdf"
FONT = "C:/Windows/Fonts/arial.ttf"

# Etiketin ilk satırı -> yazılacak satırlar. Aynı etiket birden fazla tabloda geçtiği için tablo sırası da var.
VALUES: list[dict[str, list[str]]] = [
    {  # ÖĞRENCİNİN
        "T.C. KİMLİK NO/ UYRUĞU": ["10000000146"],
        "BÖLÜMÜ": ["Bilgisayar Mühendisliği"],
        "ADI SOYADI": ["Ayşe Yılmaz"],
        "DAHA ÖNCE YAPTIĞI STAJ GÜN SAYISI": ["0"],
        "DOĞUM TARİHİ": ["10.05.2004"],
        "ÖĞRETİM YILI": ["2026-2027"],
        "ÖĞRENCİ NUMARASI": ["220101001"],
        "E-POSTA ADRESİ /TELEFON NO": ["ayse@ogrenci.edu.tr / 0555 123 45 67"],
        "İKAMETGÂH ADRESİ": ["Umuttepe Mah.", "İzmit / Kocaeli"],
    },
    {  # STAJ YAPILAN YERİN
        "Adı": ["Örnek Yazılım A.Ş."],
        "Yurtdışı Stajımı? (E/H)": ["H"],
        "Hizmet Alanı": ["Yazılım"],
        "Staj Başlama Tarihi": ["14.06.2027"],
        "Telefon No": ["0262 123 45 67"],
        "Staj Bitiş Tarihi": ["09.07.2027"],
        "Staj Gün Sayısı": ["20"],
        "E-Posta Adresi": ["ik@ornek.com.tr"],
        "Hafta Sonu Çalışılıyor mu? (E / H)": ["H"],
        "Web Adresi": ["ornek.com.tr"],
        "Çalışan Sayısı": ["45"],
        "Mühendis Sayısı": ["12"],
        "Ücret Alıyor mu? (E / H) - (**)": ["H"],
        "Adres Bilgisi": ["Kocaeli Teknopark, Başiskele / Kocaeli"],
    },
    {  # İŞVEREN VEYA YETKİLİNİN
        "Adı Soyadı": ["Mehmet Öztürk"],
        "Görev / Unvanı": ["Yazılım Müdürü"],
        "E-Posta adresi": ["mehmet@ornek.com.tr"],
        "Telefon No": ["0262 123 45 68"],
    },
]


def first_line(page: pdfplumber.page.Page, bbox: tuple[float, float, float, float]) -> str:
    text = page.crop((bbox[0] + 1, bbox[1] + 1, bbox[2] - 1, bbox[3] - 1)).extract_text() or ""
    return text.split("\n")[0].strip()


def build_filled() -> bytes:
    pdfmetrics.registerFont(TTFont("Arial", FONT))
    with pdfplumber.open(TEMPLATE) as pdf:
        page = pdf.pages[0]
        height = float(page.height)
        overlay = io.BytesIO()
        c = canvas.Canvas(overlay, pagesize=(float(page.width), height))
        c.setFont("Arial", 7.5)

        tables = page.find_tables()
        for table, values in zip(tables[:3], VALUES, strict=True):
            for row in table.rows:
                cells = row.cells
                for i in range(0, len(cells) - 1, 2):
                    if cells[i] is None or cells[i + 1] is None:
                        continue
                    lines = values.get(first_line(page, cells[i]))
                    if not lines:
                        continue
                    x0, top, x1, _ = cells[i + 1]
                    for n, line in enumerate(lines):
                        # Hücreye sığmayan satırı küçült (taşarsa komşu hücreden okunur)
                        size = 7.5
                        while pdfmetrics.stringWidth(line, "Arial", size) > x1 - x0 - 5:
                            size -= 0.25
                        c.setFont("Arial", size)
                        c.drawString(x0 + 3, height - top - 9 - n * 8.5, line)
                    c.setFont("Arial", 7.5)

        # Sağlık yardım statüsü: 2. seçeneğin yanına X
        box = next(w for w in page.extract_words() if w["text"] == "2-☐")
        c.drawString(box["x1"] + 3, height - box["bottom"] + 1, "X")

        # İşveren imza/kaşe: daire + imza eğrisi
        stamp = next(w for w in page.extract_words() if w["text"] == "Kaşe")
        c.circle(stamp["x1"] + 60, height - stamp["bottom"] + 2, 18)
        path = c.beginPath()
        path.moveTo(stamp["x1"] + 100, height - stamp["bottom"])
        path.curveTo(stamp["x1"] + 120, height - stamp["bottom"] + 15, stamp["x1"] + 130, height - stamp["bottom"] - 10, stamp["x1"] + 150, height - stamp["bottom"] + 5)
        c.drawPath(path)

        # Öğrenci onayı: tarih ve imza (soldaki onay kutusundaki ilk "Tarih:" ve "İmza:")
        words = page.extract_words()
        tarih = min((w for w in words if w["text"] == "Tarih:"), key=lambda w: w["x0"])
        imza = min((w for w in words if w["text"] == "İmza:"), key=lambda w: w["x0"])
        c.drawString(tarih["x1"] + 4, height - tarih["bottom"] + 2, "01.05.2027")
        path = c.beginPath()
        path.moveTo(imza["x1"] + 5, height - imza["bottom"] + 2)
        path.curveTo(imza["x1"] + 20, height - imza["bottom"] + 14, imza["x1"] + 30, height - imza["bottom"] - 6, imza["x1"] + 50, height - imza["bottom"] + 6)
        c.drawPath(path)

        c.save()

    writer = PdfWriter()
    base = PdfReader(TEMPLATE).pages[0]
    base.merge_page(PdfReader(io.BytesIO(overlay.getvalue())).pages[0])
    writer.add_page(base)
    out = io.BytesIO()
    writer.write(out)
    return out.getvalue()


if __name__ == "__main__":
    target = HERE / "ek16_dolu.pdf"
    target.write_bytes(build_filled())
    print(f"Yazıldı: {target}")
