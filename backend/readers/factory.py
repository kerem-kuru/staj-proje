from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from .base import DocumentReader
from .gemini import GeminiDocumentReader
from .mock import MockDocumentReader
from .pdf_form import PdfFormReader


def get_document_reader(name: str | None = None) -> DocumentReader:
    """Ayarlardaki DOCUMENT_READER değerine göre okuyucu döndürür."""
    name = name or settings.DOCUMENT_READER
    if name == PdfFormReader.name:
        return PdfFormReader()
    if name == MockDocumentReader.name:
        return MockDocumentReader()
    if name == GeminiDocumentReader.name:
        if not settings.GEMINI_API_KEY:
            raise ImproperlyConfigured("Gemini okuyucu için GEMINI_API_KEY tanımlanmalı.")
        return GeminiDocumentReader(api_key=settings.GEMINI_API_KEY)
    raise ImproperlyConfigured(f"Bilinmeyen belge okuyucu: {name}")
