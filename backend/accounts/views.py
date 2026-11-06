from typing import Any

from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import (
    RoleTokenObtainPairSerializer,
    StudentRegisterSerializer,
    UserSerializer,
    VersionedTokenRefreshSerializer,
)
from .services import LoginGuard, register_student


class LoginView(TokenObtainPairView):
    serializer_class = RoleTokenObtainPairSerializer

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        guard = LoginGuard(str(request.data.get("email", "")), request.META.get("REMOTE_ADDR"))
        guard.ensure_not_locked()
        try:
            response = super().post(request, *args, **kwargs)
        except AuthenticationFailed:
            guard.record_failure()
            guard.ensure_not_locked()  # bu deneme kilidi başlattıysa kullanıcı hemen görsün
            raise
        guard.record_success()
        return response


class RefreshView(TokenRefreshView):
    serializer_class = VersionedTokenRefreshSerializer


class LogoutView(APIView):
    def post(self, request: Request) -> Response:
        request.user.revoke_tokens()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = StudentRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = register_student(**serializer.validated_data)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class MeView(APIView):
    def get(self, request: Request) -> Response:
        return Response(UserSerializer(request.user).data)
