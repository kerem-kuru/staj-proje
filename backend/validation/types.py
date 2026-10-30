from collections.abc import Iterable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class Severity(StrEnum):
    ERROR = "error"  # belgeyi Hatalı/Eksik yapar
    WARNING = "warning"  # bilgilendirme, onayı engellemez


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    field: str | None
    message: str
    severity: Severity = Severity.ERROR

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "field": self.field, "message": self.message, "severity": str(self.severity)}


class ValidationResult:
    """Denetim sonucunu biriktirir; bulgu listesi dışarıdan değiştirilemez."""

    def __init__(self) -> None:
        self._issues: list[ValidationIssue] = []

    def extend(self, issues: Iterable[ValidationIssue]) -> None:
        self._issues.extend(issues)

    @property
    def issues(self) -> tuple[ValidationIssue, ...]:
        return tuple(self._issues)

    @property
    def errors(self) -> tuple[ValidationIssue, ...]:
        return tuple(i for i in self._issues if i.severity is Severity.ERROR)

    @property
    def warnings(self) -> tuple[ValidationIssue, ...]:
        return tuple(i for i in self._issues if i.severity is Severity.WARNING)

    @property
    def is_valid(self) -> bool:
        return not self.errors
