from typing import Any

from rest_framework import serializers

from readers.ek16 import Ek16Data
from validation.models import ValidationReport

from .models import Document
from .policies import policy_for
from .workflow import DocumentStatus, DocumentWorkflow


class ValidationReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationReport
        fields = ["id", "revision", "is_valid", "summary", "issues", "reader_name", "created_at"]


class DocumentSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    doc_type_display = serializers.CharField(source="get_doc_type_display", read_only=True)
    student_number = serializers.CharField(source="student.student_number", read_only=True)
    student_name = serializers.CharField(source="student.full_name", read_only=True)
    latest_report = serializers.SerializerMethodField()
    extracted_fields = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id",
            "doc_type",
            "doc_type_display",
            "status",
            "status_display",
            "original_filename",
            "revision",
            "student_number",
            "student_name",
            "extracted_data",
            "extracted_fields",
            "admin_note",
            "latest_report",
            "permissions",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_latest_report(self, obj: Document) -> dict | None:
        report = obj.reports.first()
        return ValidationReportSerializer(report).data if report else None

    def get_extracted_fields(self, obj: Document) -> list[dict[str, Any]]:
        """Okunan bilgiler, formdaki etiketleri ve sırasıyla."""
        if not obj.extracted_data:
            return []
        data = Ek16Data.from_dict(obj.extracted_data)
        return [
            {"name": name, "label": label, "value": obj.extracted_data.get(name), "unparsed": data.unparsed.get(name)}
            for name, label, _ in data.labeled_items()
        ]

    def get_permissions(self, obj: Document) -> dict[str, bool]:
        """Arayüzün hangi butonları göstereceğini bilmesi için."""
        user = self.context["request"].user
        policy = policy_for(user)
        can_modify = policy.can_modify(user, obj)
        return {
            "can_reupload": user.is_student
            and can_modify
            and DocumentWorkflow.can_transition(obj.status, DocumentStatus.UPLOADED),
            "can_delete": policy.can_delete(user, obj),
            "can_complete": user.is_admin and DocumentWorkflow.can_transition(obj.status, DocumentStatus.COMPLETED),
            "can_reject": user.is_admin and DocumentWorkflow.can_transition(obj.status, DocumentStatus.REJECTED),
        }


class DocumentDetailSerializer(DocumentSerializer):
    reports = ValidationReportSerializer(many=True, read_only=True)

    class Meta(DocumentSerializer.Meta):
        fields = [*DocumentSerializer.Meta.fields, "reports"]
        read_only_fields = fields


class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["file"]


class AdminNoteSerializer(serializers.Serializer):
    admin_note = serializers.CharField(allow_blank=True, max_length=2000)


class RejectSerializer(serializers.Serializer):
    note = serializers.CharField(max_length=2000)
