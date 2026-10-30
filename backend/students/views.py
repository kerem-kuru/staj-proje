from django.db.models import Q, QuerySet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.response import Response

from accounts.permissions import IsAdmin, IsStudent

from .models import StudentProfile
from .serializers import StudentImportSerializer, StudentProfileSerializer
from .services import CsvStudentImporter


class StudentProfileViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StudentProfileSerializer

    def get_permissions(self) -> list[BasePermission]:
        if self.action == "me":
            return [IsStudent()]
        return [IsAdmin()]

    def get_queryset(self) -> QuerySet[StudentProfile]:
        queryset = StudentProfile.objects.all()
        search = self.request.query_params.get("q", "").strip()
        if search:
            queryset = queryset.filter(
                Q(student_number__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )
        return queryset

    @action(detail=False, methods=["get"])
    def me(self, request: Request) -> Response:
        profile = StudentProfile.objects.filter(user=request.user).first()
        if profile is None:
            raise NotFound("Öğrenci profiliniz bulunamadı.")
        return Response(self.get_serializer(profile).data)

    @action(detail=False, methods=["post"], url_path="import")
    def import_dataset(self, request: Request) -> Response:
        serializer = StudentImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = CsvStudentImporter().import_stream(serializer.validated_data["file"])
        return Response(result.to_dict(), status=status.HTTP_200_OK)
