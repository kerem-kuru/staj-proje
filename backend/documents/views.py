from django.db.models import QuerySet
from django.http import FileResponse
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer

from accounts.permissions import IsAdmin, IsStudent
from students.models import StudentProfile

from .models import Document
from .policies import policy_for
from .serializers import (
    AdminNoteSerializer,
    DocumentDetailSerializer,
    DocumentSerializer,
    DocumentUploadSerializer,
    EngineerDepartmentSerializer,
    RejectSerializer,
)
from .services.document_service import DocumentService
from .workflow import DocumentStatus


class DocumentViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    """Öğrenci kendi belgelerini, admin tüm belgeleri görür. İş kuralları DocumentService'tedir."""

    ADMIN_ACTIONS = {"partial_update", "complete", "reject"}
    STUDENT_ACTIONS = {"create", "reupload", "engineer_department"}

    def get_permissions(self) -> list[BasePermission]:
        if self.action in self.ADMIN_ACTIONS:
            return [IsAdmin()]
        if self.action in self.STUDENT_ACTIONS:
            return [IsStudent()]
        return [IsAuthenticated()]

    def get_queryset(self) -> QuerySet[Document]:
        queryset = Document.objects.select_related("student").prefetch_related("reports")
        queryset = policy_for(self.request.user).scope(queryset, self.request.user)
        status_filter = self._status_param("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        excluded = self._status_param("exclude_status")
        if excluded:
            queryset = queryset.exclude(status=excluded)
        return queryset

    def _status_param(self, name: str) -> str | None:
        value = self.request.query_params.get(name)
        if value and value not in DocumentStatus.values:
            raise ValidationError({name: [f"Geçersiz statü: {value}"]})
        return value

    def get_serializer_class(self) -> type[BaseSerializer]:
        return DocumentDetailSerializer if self.action == "retrieve" else DocumentSerializer

    def _service(self) -> DocumentService:
        return DocumentService()

    def _detail_response(self, document: Document, code: int = status.HTTP_200_OK) -> Response:
        document = self.get_queryset().get(pk=document.pk)
        return Response(DocumentDetailSerializer(document, context=self.get_serializer_context()).data, status=code)

    def create(self, request: Request) -> Response:
        profile = StudentProfile.objects.filter(user=request.user).first()
        if profile is None:
            raise NotFound("Öğrenci profiliniz bulunamadı.")
        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = self._service().upload(profile, **serializer.validated_data)
        return self._detail_response(document, status.HTTP_201_CREATED)

    def partial_update(self, request: Request, pk: str | None = None) -> Response:
        serializer = AdminNoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = self._service().update_note(request.user, self.get_object(), serializer.validated_data["admin_note"])
        return self._detail_response(document)

    def destroy(self, request: Request, pk: str | None = None) -> Response:
        self._service().delete(request.user, self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=["post"])
    def reupload(self, request: Request, pk: str | None = None) -> Response:
        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = self._service().reupload(request.user, self.get_object(), **serializer.validated_data)
        return self._detail_response(document)

    @action(detail=True, methods=["post"], url_path="engineer-department")
    def engineer_department(self, request: Request, pk: str | None = None) -> Response:
        serializer = EngineerDepartmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        department = serializer.validated_data["engineer_department"]
        document = self._service().set_engineer_department(request.user, self.get_object(), department)
        return self._detail_response(document)

    @action(detail=True, methods=["post"])
    def complete(self, request: Request, pk: str | None = None) -> Response:
        document = self._service().complete(self.get_object())
        return self._detail_response(document)

    @action(detail=True, methods=["post"])
    def reject(self, request: Request, pk: str | None = None) -> Response:
        serializer = RejectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = self._service().reject(self.get_object(), serializer.validated_data["note"])
        return self._detail_response(document)

    @action(detail=True, methods=["get"])
    def download(self, request: Request, pk: str | None = None) -> FileResponse:
        document = self.get_object()
        if not document.file:
            raise NotFound("Belgeye ait dosya bulunamadı.")
        return FileResponse(document.file.open("rb"), as_attachment=True, filename=document.original_filename)
