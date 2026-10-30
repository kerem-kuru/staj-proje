"""Formdan okunan ham metni tipli değerlere çeviren yardımcılar.

Her ayrıştırıcı boş metin için None döndürür, anlaşılamayan metin için ValueError fırlatır.
Okuyucular (PDF, ileride Gemini) aynı kuralları paylaşsın diye ortak tutulur.
"""
import re
from datetime import date

_CIRCUMFLEX = str.maketrans({"â": "a", "Â": "A", "î": "i", "Î": "İ", "û": "u", "Û": "U"})
_DMY_RE = re.compile(r"(\d{1,2})[./-](\d{1,2})[./-](\d{4}|\d{2})")
_YMD_RE = re.compile(r"(\d{4})-(\d{1,2})-(\d{1,2})")
_EMAIL_RE = re.compile(r"[^@\s/;,]+@[^@\s/;,]+\.[^@\s/;,]+")
_CHECK_MARKS = "☒☑✓✔✗✘■●"


def normalize_tr(text: str) -> str:
    """Türkçe büyük/küçük harf (İ/i, I/ı), şapkalı harf ve boşluk farklarını yok sayar."""
    text = text.translate(_CIRCUMFLEX).replace("I", "ı").replace("İ", "i")
    return " ".join(text.lower().split())


def clean(text: str | None) -> str:
    return " ".join((text or "").split())


def parse_text(text: str | None) -> str | None:
    return clean(text) or None


def parse_date(text: str | None, today: date | None = None) -> date | None:
    """GG.AA.YYYY, GG/AA/YYYY, GG-AA-YYYY, YYYY-AA-GG ve iki haneli yıl kabul edilir."""
    compact = clean(text).replace(" ", "")
    if not compact:
        return None
    if match := _YMD_RE.fullmatch(compact):
        year, month, day = (int(part) for part in match.groups())
    elif match := _DMY_RE.fullmatch(compact):
        day, month = int(match.group(1)), int(match.group(2))
        year = int(match.group(3))
        if len(match.group(3)) == 2:
            current = (today or date.today()).year
            year += 2000 if 2000 + year <= current + 10 else 1900
    else:
        raise ValueError(text)
    return date(year, month, day)


def parse_int(text: str | None) -> int | None:
    """'20', '20 gün', '1.250' gibi tek bir sayı içeren metni okur."""
    value = clean(text)
    if not value:
        return None
    value = re.sub(r"(?<=\d)[.,](?=\d{3}\b)", "", value)  # binlik ayırıcı
    numbers = re.findall(r"\d+", value)
    if len(numbers) != 1:
        raise ValueError(text)
    return int(numbers[0])


def parse_yes_no(text: str | None) -> bool | None:
    value = normalize_tr(clean(text)).strip(" .()")
    if not value:
        return None
    if value in {"e", "evet"}:
        return True
    if value in {"h", "hayır", "hayir"}:
        return False
    raise ValueError(text)


def parse_choice(text: str | None, options: range) -> int | None:
    """'1-☐ 2-☒ ...' biçimindeki onay kutularından işaretli olanı döndürür.

    Kutu içine ☒/☑/✓ konması ya da yanına X yazılması işaret sayılır.
    Hiçbiri işaretli değilse None, birden fazlası işaretliyse ValueError.
    """
    value = text or ""
    selected: list[int] = []
    saw_options = False
    for line in value.splitlines():
        match = re.match(r"^\s*(\d)\s*-\s*(.*)$", line)
        if not match or int(match.group(1)) not in options:
            continue
        saw_options = True
        rest = match.group(2)
        if any(mark in rest for mark in _CHECK_MARKS) or rest.replace("☐", "").strip():
            selected.append(int(match.group(1)))
    if not saw_options:
        single = clean(value)
        if not single:
            return None
        if single.isdigit() and int(single) in options:
            return int(single)
        raise ValueError(text)
    if len(selected) > 1:
        raise ValueError(text)
    return selected[0] if selected else None


def split_contact(text: str | None) -> tuple[str | None, str | None]:
    """'E-posta adresi / telefon no' hücresini (e-posta, telefon) olarak ayırır."""
    value = clean(text)
    email_match = _EMAIL_RE.search(value)
    email = email_match.group(0) if email_match else None
    rest = value.replace(email, " ") if email else value
    phone = clean(re.sub(r"^[\s/;,|-]+|[\s/;,|-]+$", "", rest)) or None
    return email, phone
