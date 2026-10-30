"""Gemini tabanlı okuyucu — final aşamasında doldurulacak (ROADMAP)."""
from typing import TYPE_CHECKING

from .base import DocumentReader, ReaderError
from .ek16 import Ek16Data

if TYPE_CHECKING:
    from documents.models import Document


class GeminiDocumentReader(DocumentReader):
    name = "gemini"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    def _extract(self, content: bytes, document: "Document") -> Ek16Data:
        raise ReaderError("Gemini okuyucu henüz etkin değil.")
