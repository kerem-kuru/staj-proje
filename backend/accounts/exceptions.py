from rest_framework import status
from rest_framework.exceptions import APIException


class AccountLocked(APIException):
    status_code = status.HTTP_423_LOCKED
    default_code = "account_locked"

    def __init__(self, minutes_left: int) -> None:
        super().__init__(
            f"Çok fazla hatalı giriş denemesi yapıldı; hesap kilitlendi. {minutes_left} dakika sonra tekrar deneyin."
        )
