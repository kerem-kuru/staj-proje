from rest_framework import serializers

from documents.file_validators import FileExtensionTr

from .models import StudentProfile


class StudentProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    has_account = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = [
            "id",
            "student_number",
            "first_name",
            "last_name",
            "full_name",
            "department",
            "class_year",
            "email",
            "has_account",
        ]
        read_only_fields = fields

    def get_has_account(self, obj: StudentProfile) -> bool:
        return obj.user_id is not None


class StudentImportSerializer(serializers.Serializer):
    file = serializers.FileField(validators=[FileExtensionTr(["csv"])])
