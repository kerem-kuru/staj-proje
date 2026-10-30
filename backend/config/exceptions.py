"""Tüm API hatalarını aynı JSON biçiminde döndüren DRF exception handler'ı.

Biçim: {"detail": "<Türkçe özet>", "errors": {<alan>: [<mesajlar>]} | null}
"""
import logging
from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def json_exception_handler(exc: Exception, context: dict[str, Any]) -> Response:
    if isinstance(exc, DjangoValidationError):
        exc = ValidationError(exc.message_dict if hasattr(exc, "error_dict") else exc.messages)

    response = exception_handler(exc, context)
    if response is None:
        logger.exception("Beklenmeyen sunucu hatası", exc_info=exc)
        return Response(
            {"detail": "Beklenmeyen bir sunucu hatası oluştu.", "errors": None},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(exc, ValidationError):
        errors = response.data if isinstance(response.data, dict) else {"non_field_errors": response.data}
        response.data = {"detail": "Gönderilen veriler geçersiz.", "errors": errors}
    else:
        detail = response.data.get("detail", "") if isinstance(response.data, dict) else response.data
        response.data = {"detail": str(detail), "errors": None}
    return response
