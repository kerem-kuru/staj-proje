from typing import Any

from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import Token

TOKEN_VERSION_CLAIM = "tv"


class VersionedJWTAuthentication(JWTAuthentication):
    """Çıkış yapıldığında süresi dolmamış erişim token'larını da reddeder."""

    def get_user(self, validated_token: Token) -> Any:
        user = super().get_user(validated_token)
        if validated_token.get(TOKEN_VERSION_CLAIM) != user.token_version:
            raise AuthenticationFailed("Oturum sonlandırılmış. Lütfen yeniden giriş yapın.", code="token_revoked")
        return user
