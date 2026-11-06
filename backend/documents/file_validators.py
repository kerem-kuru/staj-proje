"""Yüklenen dosyalar için doğrulayıcılar (Django field validator'ları)."""
from collections.abc import Sequence
from pathlib import Path
from typing import ClassVar

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.utils.deconstruct import deconstructible


@deconstructible
class FileExtensionTr:
    def __init__(self, allowed: Sequence[str] | None = None) -> None:
        self.allowed = [ext.lower() for ext in allowed] if allowed else None

    def _allowed(self) -> list[str]:
        return self.allowed or settings.DOCUMENT_UPLOAD["ALLOWED_EXTENSIONS"]

    def __call__(self, file: File) -> None:
        extension = Path(file.name or "").suffix.lstrip(".").lower()
        if extension not in self._allowed():
            raise ValidationError(
                f"Desteklenmeyen dosya türü. İzin verilenler: {', '.join(self._allowed())}.",
                code="invalid_extension",
            )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, FileExtensionTr) and self.allowed == other.allowed


@deconstructible
class MaxFileSize:
    def __init__(self, max_mb: int | None = None) -> None:
        self.max_mb = max_mb

    def __call__(self, file: File) -> None:
        max_mb = self.max_mb or settings.DOCUMENT_UPLOAD["MAX_SIZE_MB"]
        if file.size is not None and file.size > max_mb * 1024 * 1024:
            raise ValidationError(f"Dosya boyutu {max_mb} MB'ı aşamaz.", code="file_too_large")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, MaxFileSize) and self.max_mb == other.max_mb


@deconstructible
class FileSignature:
    """Dosya içeriğinin uzantısıyla uyuştuğunu ilk baytlardan kontrol eder."""

    SIGNATURES: ClassVar[dict[str, tuple[bytes, ...]]] = {
        "pdf": (b"%PDF",),
        "doc": (b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",),
        "docx": (b"PK\x03\x04",),
        "png": (b"\x89PNG\r\n\x1a\n",),
        "jpg": (b"\xff\xd8\xff",),
        "jpeg": (b"\xff\xd8\xff",),
    }

    def __call__(self, file: File) -> None:
        extension = Path(file.name or "").suffix.lstrip(".").lower()
        expected = self.SIGNATURES.get(extension)
        if expected is None:
            return
        position = file.tell() if hasattr(file, "tell") else 0
        file.seek(0)
        head = file.read(8)
        file.seek(position)
        if not head.startswith(expected):
            raise ValidationError("Dosya içeriği uzantısıyla uyuşmuyor veya dosya bozuk.", code="invalid_signature")

    def __eq__(self, other: object) -> bool:
        return isinstance(other, FileSignature)
