from typing import TYPE_CHECKING

from .models import ValidationReport
from .types import ValidationIssue, ValidationResult

if TYPE_CHECKING:
    from documents.models import Document


def summarize(result: ValidationResult) -> str:
    if result.is_valid and not result.warnings:
        return "Belge tüm kontrollerden geçti."
    parts = []
    if result.errors:
        parts.append(f"{len(result.errors)} hata")
    if result.warnings:
        parts.append(f"{len(result.warnings)} uyarı")
    return f"{' ve '.join(parts)} bulundu."


def create_report(document: "Document", result: ValidationResult, reader_name: str) -> ValidationReport:
    return ValidationReport.objects.create(
        document=document,
        revision=document.revision,
        is_valid=result.is_valid,
        summary=summarize(result),
        issues=[issue.to_dict() for issue in result.issues],
        reader_name=reader_name,
    )


def create_reader_failure_report(document: "Document", message: str, reader_name: str) -> ValidationReport:
    result = ValidationResult()
    result.extend([ValidationIssue(code="reader_error", field=None, message=message)])
    return create_report(document, result, reader_name)
