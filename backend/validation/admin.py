from django.contrib import admin

from .models import ValidationReport


@admin.register(ValidationReport)
class ValidationReportAdmin(admin.ModelAdmin):
    list_display = ["document", "revision", "is_valid", "summary", "reader_name", "created_at"]
    list_filter = ["is_valid", "reader_name"]
    readonly_fields = ["document", "revision", "is_valid", "summary", "issues", "reader_name", "created_at"]
