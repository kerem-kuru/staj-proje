"""Belge okuyucu soyutlaması.

Sistemin geri kalanı yalnızca `DocumentReader.read()` ile konuşur; belgenin
sahte veriyle mi, Gemini ile mi, başka bir modelle mi okunduğunu bilmez.
Yeni bir sağlayıcı eklemek = yeni bir alt sınıf + factory kaydı.
"""
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar

from .ek16 import Ek16Data

if TYPE_CHECKING:
    from documents.models import Document


class ReaderError(Exception):
    """Belge okunamadığında fırlatılır; mesajı kullanıcıya gösterilir."""


class DocumentReader(ABC):
    name: ClassVar[str]

    def read(self, document: "Document") -> Ek16Data:
        """Şablon metot: dosyayı açar, okumayı alt sınıfa bırakır."""
        if not document.file:
            raise ReaderError("Belgeye ait dosya bulunamadı.")
        try:
            with document.file.open("rb") as stream:
                content = stream.read()
        except OSError as exc:
            raise ReaderError("Belge dosyası açılamadı.") from exc
        return self._extract(content, document)

    @abstractmethod
    def _extract(self, content: bytes, document: "Document") -> Ek16Data:
        """Dosya içeriğinden Ek-16 alanlarını çıkarır."""
