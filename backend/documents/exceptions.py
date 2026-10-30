from rest_framework import status
from rest_framework.exceptions import APIException, PermissionDenied


class InvalidStatusTransition(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "Belgenin statüsü bu işleme uygun değil."
    default_code = "invalid_status_transition"


class DocumentLocked(PermissionDenied):
    default_detail = "Tamamlanan belge öğrenci tarafından değiştirilemez veya silinemez."
    default_code = "document_locked"
