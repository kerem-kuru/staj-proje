from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import LoginAttempt, LoginLock, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ["email"]
    list_display = ["email", "first_name", "last_name", "role", "is_active"]
    list_filter = ["role", "is_active"]
    search_fields = ["email", "first_name", "last_name"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Kişisel bilgiler", {"fields": ("first_name", "last_name")}),
        ("Yetki", {"fields": ("role", "is_active", "is_staff", "is_superuser")}),
        ("Tarihler", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "first_name", "last_name", "role", "password1", "password2")}),
    )


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ["created_at", "email", "ip_address", "succeeded"]
    list_filter = ["succeeded"]
    search_fields = ["email"]


@admin.register(LoginLock)
class LoginLockAdmin(admin.ModelAdmin):
    list_display = ["email", "failures", "locked_until"]
    search_fields = ["email"]
