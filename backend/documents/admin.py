from django.contrib import admin

from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ["id", "student", "doc_type", "status", "revision", "created_at"]
    list_filter = ["status", "doc_type"]
    search_fields = ["student__student_number", "student__first_name", "student__last_name"]
    # Statü yalnızca API/servis üzerinden, akış kurallarına uygun değişir.
    readonly_fields = ["status", "revision", "extracted_data", "created_at", "updated_at"]
