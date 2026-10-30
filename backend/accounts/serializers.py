from typing import Any

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import Token

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name", "role"]
        read_only_fields = fields


class StudentRegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    student_number = serializers.CharField(max_length=20)

    def validate_password(self, value: str) -> str:
        validate_password(value)
        return value


class RoleTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Erişim token'ına kullanıcının rolünü ekler."""

    default_error_messages = {"no_active_account": "E-posta veya şifre hatalı."}

    @classmethod
    def get_token(cls, user: Any) -> Token:
        token = super().get_token(user)
        token["role"] = user.role
        return token
