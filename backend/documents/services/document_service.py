"""Belge iş akışı: yükleme, denetim, yeniden yükleme, tamamlama, silme.

View'lar yalnızca bu servisi çağırır; statü ve yetki kuralları burada uygulanır.
"""
import logging

from django.core.files.uploadedfile import UploadedFile
from django.db import transaction
from rest_framework.exceptions import ValidationError

from accounts.models import User
from readers.base import DocumentReader, ReaderError
from readers.factory import get_document_reader
from students.models import StudentProfile
from validation.context import ValidationContext
from validation.engine import ValidationEngine
from validation.reports import create_reader_failure_report, create_report

from ..exceptions import DocumentLocked
from ..models import Document
from ..policies import policy_for
from ..workflow import DocumentStatus

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self, reader: DocumentReader | None = None, engine: ValidationEngine | None = None) -> None:
        self._reader = reader or get_document_reader()
        self._engine = engine or ValidationEngine.default()

    # --- Öğrenci işlemleri -----------------------------------------------

    def upload(self, student: StudentProfile, file: UploadedFile) -> Document:
        with transaction.atomic():
            document = Document.objects.create(student=student, file=file, original_filename=file.name)
        return self.process(document)

    def reupload(self, user: User, document: Document, file: UploadedFile) -> Document:
        self._ensure_can_modify(user, document)
        old_file_name = document.file.name
        with transaction.atomic():
            document.replace_file(file)
            document.save()
        if old_file_name:
            document.file.storage.delete(old_file_name)
        return self.process(document)

    # --- Denetim ------------------------------------------------------------

    def process(self, document: Document) -> Document:
        """Belgeyi okur, kurallara göre denetler ve sonuca göre statüsünü belirler."""
        with transaction.atomic():
            document.transition_to(DocumentStatus.IN_REVIEW)
            document.save(update_fields=["status", "updated_at"])

            try:
                data = self._reader.read(document)
            except ReaderError as exc:
                logger.warning("Belge #%s okunamadı: %s", document.pk, exc)
                create_reader_failure_report(document, str(exc), self._reader.name)
                document.transition_to(DocumentStatus.REJECTED)
                document.save(update_fields=["status", "updated_at"])
                return document

            result = self._engine.run(data, ValidationContext.for_document(document))
            create_report(document, result, self._reader.name)
            document.extracted_data = data.to_dict()
            document.transition_to(DocumentStatus.APPROVED if result.is_valid else DocumentStatus.REJECTED)
            document.save(update_fields=["status", "extracted_data", "updated_at"])
        return document

    # --- Admin işlemleri ------------------------------------------------------

    def complete(self, document: Document) -> Document:
        document.transition_to(DocumentStatus.COMPLETED)
        document.save(update_fields=["status", "updated_at"])
        return document

    def reject(self, document: Document, note: str) -> Document:
        if not note.strip():
            raise ValidationError({"note": ["Geri çevirme gerekçesi yazılmalı."]})
        document.transition_to(DocumentStatus.REJECTED)
        document.admin_note = note.strip()
        document.save(update_fields=["status", "admin_note", "updated_at"])
        return document

    def update_note(self, user: User, document: Document, note: str) -> Document:
        self._ensure_can_modify(user, document)
        document.admin_note = note.strip()
        document.save(update_fields=["admin_note", "updated_at"])
        return document

    # --- Ortak ------------------------------------------------------------------

    def delete(self, user: User, document: Document) -> None:
        if not policy_for(user).can_delete(user, document):
            raise DocumentLocked() if document.is_completed else DocumentLocked("Bu belgeyi silme yetkiniz yok.")
        file_name = document.file.name
        document.delete()
        if file_name:
            document.file.storage.delete(file_name)

    def _ensure_can_modify(self, user: User, document: Document) -> None:
        if not policy_for(user).can_modify(user, document):
            raise DocumentLocked() if document.is_completed else DocumentLocked("Bu belgeyi değiştirme yetkiniz yok.")
