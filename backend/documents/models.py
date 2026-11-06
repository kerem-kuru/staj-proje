import uuid
from datetime import date
from pathlib import Path
from typing import Any

from django.db import models

from students.models import StudentProfile

from .file_validators import FileExtensionTr, FileSignature, MaxFileSize
from .services.internship_plan import HolidayCalendar, InternshipPlan
from .workflow import DocumentStatus, DocumentWorkflow


class DocumentType(models.TextChoices):
    # Sistem şimdilik yalnızca Ek-16 işler.
    EK16 = "EK16", "Ek-16 Staj Başvuru Belgesi"


def document_upload_path(instance: "Document", filename: str) -> str:
    return f"documents/{instance.student_id}/{uuid.uuid4().hex}{Path(filename).suffix.lower()}"


class Document(models.Model):
    """Öğrencinin yüklediği Ek-16 belgesi.

    Statü yalnızca `transition_to` ile değişir; `save` kalıcı statüden yeni
    statüye geçişin akışa uygun olduğunu bir kez daha doğrular.
    """

    student = models.ForeignKey(
        StudentProfile, verbose_name="öğrenci", on_delete=models.CASCADE, related_name="documents"
    )
    doc_type = models.CharField(
        "belge türü", max_length=10, choices=DocumentType.choices, default=DocumentType.EK16, editable=False
    )
    file = models.FileField(
        "dosya",
        upload_to=document_upload_path,
        validators=[FileExtensionTr(), MaxFileSize(), FileSignature()],
    )
    original_filename = models.CharField("orijinal dosya adı", max_length=255)
    status = models.CharField(
        "statü", max_length=20, choices=DocumentStatus.choices, default=DocumentStatus.UPLOADED, editable=False
    )
    revision = models.PositiveIntegerField("revizyon", default=1)
    extracted_data = models.JSONField("okunan bilgiler", default=dict, blank=True)
    admin_note = models.TextField("yönetici notu", blank=True)
    # Öğrencinin yükleme sırasında seçtiği staj planı; belgedeki tarih ve gün sayısıyla karşılaştırılır.
    plan_start = models.DateField("seçilen başlangıç", null=True, blank=True)
    plan_end = models.DateField("seçilen bitiş", null=True, blank=True)
    plan_weekdays = models.JSONField("seçilen haftalık günler", default=list, blank=True)
    engineer_department = models.CharField("mühendisin mezun olduğu bölüm", max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "belge"
        verbose_name_plural = "belgeler"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._persisted_status: str | None = self.status if self.pk else None

    def __str__(self) -> str:
        return f"{self.get_doc_type_display()} #{self.pk} ({self.get_status_display()})"

    @property
    def is_completed(self) -> bool:
        return self.status == DocumentStatus.COMPLETED

    @property
    def needs_engineer_department(self) -> bool:
        """Mühendis sayısı 5'in altındaysa mühendisin mezun olduğu bölüm sorulur."""
        count = self.extracted_data.get("engineer_count")
        return count is not None and 1 <= count < 5

    def selected_plan(self, calendar: HolidayCalendar) -> InternshipPlan | None:
        if self.plan_start is None or self.plan_end is None:
            return None
        return InternshipPlan(self.plan_start, self.plan_end, frozenset(self.plan_weekdays), calendar)

    def transition_to(self, target: DocumentStatus) -> None:
        DocumentWorkflow.ensure_transition(self.status, target)
        self.status = target

    def replace_file(self, new_file: Any, plan_start: date, plan_end: date, plan_weekdays: list[int]) -> None:
        """Hatalı/Eksik belgenin düzeltilmiş halini alır ve akışı başa sarar."""
        self.transition_to(DocumentStatus.UPLOADED)
        self.file = new_file
        self.plan_start, self.plan_end, self.plan_weekdays = plan_start, plan_end, plan_weekdays
        self.original_filename = new_file.name
        self.revision += 1
        self.extracted_data = {}

    def save(self, *args: Any, **kwargs: Any) -> None:
        if self._persisted_status is not None and self._persisted_status != self.status:
            DocumentWorkflow.ensure_transition(self._persisted_status, self.status)
        super().save(*args, **kwargs)
        self._persisted_status = self.status

    def refresh_from_db(self, *args: Any, **kwargs: Any) -> None:
        super().refresh_from_db(*args, **kwargs)
        self._persisted_status = self.status
