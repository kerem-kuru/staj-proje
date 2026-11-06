from typing import Any

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token

from .authentication import TOKEN_VERSION_CLAIM
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
        token[TOKEN_VERSION_CLAIM] = user.token_version
        return token


class VersionedTokenRefreshSerializer(TokenRefreshSerializer):
    """Çıkış yapıldıktan sonra eski yenileme token'ıyla yeni erişim token'ı alınmasını engeller."""

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        token = self.token_class(attrs["refresh"])
        user = User.objects.filter(pk=token.get(api_settings.USER_ID_CLAIM)).first()
        if user is None or token.get(TOKEN_VERSION_CLAIM) != user.token_version:
            raise InvalidToken("Oturum sonlandırılmış. Lütfen yeniden giriş yapın.")
        return super().validate(attrs)
