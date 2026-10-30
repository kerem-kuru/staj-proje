"""Ek-17 üretimi — final aşamasında doldurulacak (ROADMAP).

Ek-17 yalnızca "Tamamlandı" statüsündeki Ek-16 belgelerinden üretilir.
Çıktı biçimi (Excel/Word/PDF) netleştiğinde `Ek17Exporter` alt sınıfı yazılır.
"""
from abc import ABC, abstractmethod
from typing import ClassVar

from django.db.models import QuerySet

from documents.models import Document
from documents.workflow import DocumentStatus


def completed_documents() -> QuerySet[Document]:
    return Document.objects.filter(status=DocumentStatus.COMPLETED).select_related("student")


class Ek17Exporter(ABC):
    content_type: ClassVar[str]
    file_extension: ClassVar[str]

    @abstractmethod
    def export(self, documents: QuerySet[Document]) -> bytes:
        """Tamamlanmış belgelerden Ek-17 dosyasının içeriğini üretir."""
