"""Rol tabanlı DRF izin sınıfları.

`RolePermission` ortak davranışı tanımlar; alt sınıflar yalnızca hangi rolün
gerektiğini ve Türkçe hata mesajını belirler (kalıtım).
"""
from typing import ClassVar

from django.core.exceptions import ImproperlyConfigured
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from .models import Role


class RolePermission(BasePermission):
    required_role: ClassVar[Role | None] = None
    message = "Bu işlem için yetkiniz yok."

    def has_permission(self, request: Request, view: APIView) -> bool:
        if self.required_role is None:
            raise ImproperlyConfigured(f"{type(self).__name__} için required_role tanımlanmalı.")
        user = request.user
        return bool(user and user.is_authenticated and user.has_role(self.required_role))


class IsStudent(RolePermission):
    required_role = Role.STUDENT
    message = "Bu işlem yalnızca öğrenciler tarafından yapılabilir."


class IsAdmin(RolePermission):
    required_role = Role.ADMIN
    message = "Bu işlem yalnızca yöneticiler tarafından yapılabilir."
