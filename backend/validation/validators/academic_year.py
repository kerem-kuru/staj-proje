import re
from datetime import date

from readers.ek16 import Ek16Data
from readers.parsing import normalize_tr

from ..context import ValidationContext
from ..types import ValidationIssue
from .base import BaseValidator

_YEAR_RE = re.compile(r"(\d{4})\s*-\s*(\d{4}) (güz|bahar|yaz)")


class AcademicYearValidator(BaseValidator):
    """'2026-2027 Güz' biçimi, ardışık yıllar, veri setindeki teslim yılı ve staj tarihleriyle uyum."""

    code = "academic_year"
    description = "Öğretim yılı ve yarıyıl bilgisinin tutarlı olması"

    def validate(self, data: Ek16Data, context: ValidationContext) -> list[ValidationIssue]:
        if not data.academic_year:
            return []
        match = _YEAR_RE.fullmatch(normalize_tr(data.academic_year))
        if match is None:
            return [
                self._issue(
                    "academic_year", "Öğretim yılı yarıyıl bilgisiyle birlikte yazılmalı (ör. 2026-2027 Güz)."
                )
            ]
        first, second = int(match.group(1)), int(match.group(2))
        if second != first + 1:
            return [self._issue("academic_year", "Öğretim yılındaki yıllar ardışık olmalı (ör. 2026-2027).")]

        issues: list[ValidationIssue] = []
        expected = context.student.submission_year if context.student else ""
        if expected and expected != f"{first}-{second}":
            issues.append(
                self._issue("academic_year", f"Belgedeki öğretim yılı veri setindeki teslim yılıyla ({expected}) uyuşmuyor.")
            )
        # Öğretim yılı eylülde başlar; yaz stajları bir sonraki eylül sonuna kadar sayılır.
        period_start, period_end = date(first, 9, 1), date(second, 9, 30)
        dates = [day for day in (data.start_date, data.end_date) if day is not None]
        if any(not period_start <= day <= period_end for day in dates):
            issues.append(self._issue("academic_year", f"Staj tarihleri {first}-{second} öğretim yılı ile uyumlu değil."))
        return issues
