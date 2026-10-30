from django.contrib import admin

from .models import StudentProfile


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ["student_number", "first_name", "last_name", "department", "class_year", "user"]
    search_fields = ["student_number", "first_name", "last_name"]
    list_filter = ["department", "class_year"]
