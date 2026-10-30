"""Google Form kontrol/gönderim — final aşamasında doldurulacak (ROADMAP).

Form sağlayıcısı soyut bir geçit (gateway) arkasında tutulur; Google Forms
dışında bir sağlayıcıya geçmek yalnızca yeni bir alt sınıf gerektirir.
"""
from abc import ABC, abstractmethod

from documents.models import Document
from students.models import StudentProfile


class InternshipFormGateway(ABC):
    @abstractmethod
    def has_submitted(self, student: StudentProfile) -> bool:
        """Öğrencinin staj formunu doldurup doldurmadığını döndürür."""

    @abstractmethod
    def submit(self, document: Document) -> None:
        """Onaylanan belgenin bilgilerini forma gönderir."""
