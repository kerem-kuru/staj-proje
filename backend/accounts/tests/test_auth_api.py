from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIRequestFactory

from accounts.models import LoginAttempt, LoginLock, Role
from accounts.permissions import IsAdmin, IsStudent

REGISTER = "/api/auth/register/"
LOGIN = "/api/auth/login/"
LOGOUT = "/api/auth/logout/"
REFRESH = "/api/auth/refresh/"
ME = "/api/auth/me/"
PASSWORD = "Gizli.12345"

PAYLOAD = {
    "email": "ayse@ogrenci.edu.tr",
    "password": "Guclu.Sifre.42",
    "first_name": "Ayşe",
    "last_name": "Yılmaz",
    "student_number": "220101001",
}


@pytest.mark.django_db
class TestRegister:
    def test_student_in_dataset_can_register_and_login(self, api_client, student_profile):
        response = api_client.post(REGISTER, PAYLOAD, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["role"] == Role.STUDENT

        student_profile.refresh_from_db()
        assert student_profile.user is not None

        login = api_client.post(LOGIN, {"email": PAYLOAD["email"], "password": PAYLOAD["password"]}, format="json")
        assert login.status_code == status.HTTP_200_OK
        assert {"access", "refresh"} <= login.data.keys()

    def test_unknown_student_number(self, api_client, db):
        response = api_client.post(REGISTER, PAYLOAD, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["errors"]["student_number"] == ["Öğrenci numarası öğrenci veri setinde bulunamadı."]

    def test_cannot_claim_profile_twice(self, api_client, student_user):
        response = api_client.post(REGISTER, {**PAYLOAD, "email": "baska@ogrenci.edu.tr"}, format="json")
        assert response.data["errors"]["student_number"] == ["Bu öğrenci numarası için zaten bir hesap var."]

    def test_wrong_password_message_is_turkish(self, api_client, student_user):
        response = api_client.post(LOGIN, {"email": student_user.email, "password": "yanlis"}, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["detail"] == "E-posta veya şifre hatalı."


def login(client, user, password=PASSWORD):
    return client.post(LOGIN, {"email": user.email, "password": password}, format="json")


@pytest.mark.django_db
class TestLoginLock:
    def test_password_is_stored_hashed(self, student_user):
        assert student_user.password != PASSWORD
        assert student_user.check_password(PASSWORD)

    def test_failed_and_successful_logins_are_logged(self, api_client, student_user):
        login(api_client, student_user, "yanlis")
        login(api_client, student_user)

        assert [a.succeeded for a in LoginAttempt.objects.order_by("created_at")] == [False, True]
        assert LoginAttempt.objects.first().email == student_user.email

    def test_five_failures_lock_the_account(self, api_client, student_user):
        statuses = [login(api_client, student_user, "yanlis").status_code for _ in range(5)]
        assert statuses == [401, 401, 401, 401, 423]

        response = login(api_client, student_user)  # doğru şifre de reddedilir
        assert response.status_code == status.HTTP_423_LOCKED
        assert "kilitlendi" in response.data["detail"]

    def test_lock_expires(self, api_client, student_user):
        for _ in range(5):
            login(api_client, student_user, "yanlis")
        LoginLock.objects.update(locked_until=timezone.now() - timedelta(seconds=1))

        assert login(api_client, student_user).status_code == status.HTTP_200_OK
        assert not LoginLock.objects.exists()

    def test_failure_after_expiry_starts_counting_again(self, api_client, student_user):
        for _ in range(5):
            login(api_client, student_user, "yanlis")
        LoginLock.objects.update(locked_until=timezone.now() - timedelta(seconds=1))

        assert login(api_client, student_user, "yanlis").status_code == status.HTTP_401_UNAUTHORIZED
        assert LoginLock.objects.get().failures == 1

    def test_success_resets_the_counter(self, api_client, student_user):
        for _ in range(4):
            login(api_client, student_user, "yanlis")
        login(api_client, student_user)

        assert login(api_client, student_user, "yanlis").status_code == status.HTTP_401_UNAUTHORIZED

    def test_unknown_email_is_counted_too(self, api_client, db):
        for _ in range(5):
            response = api_client.post(LOGIN, {"email": "yok@staj.local", "password": "x"}, format="json")
        assert response.status_code == status.HTTP_423_LOCKED

    def test_email_case_does_not_bypass_the_lock(self, api_client, student_user):
        for _ in range(5):
            login(api_client, student_user, "yanlis")
        response = api_client.post(LOGIN, {"email": student_user.email.upper(), "password": PASSWORD}, format="json")
        assert response.status_code == status.HTTP_423_LOCKED


@pytest.mark.django_db
class TestLogout:
    def _authorize(self, client, user):
        tokens = login(client, user).data
        client.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")
        return tokens

    def test_access_token_carries_the_role(self, api_client, student_user):
        self._authorize(api_client, student_user)
        assert api_client.get(ME).status_code == status.HTTP_200_OK

    def test_logout_invalidates_access_token(self, api_client, student_user):
        self._authorize(api_client, student_user)

        assert api_client.post(LOGOUT).status_code == status.HTTP_204_NO_CONTENT
        assert api_client.get(ME).status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_invalidates_refresh_token(self, api_client, student_user):
        tokens = self._authorize(api_client, student_user)
        api_client.post(LOGOUT)
        api_client.credentials()

        response = api_client.post(REFRESH, {"refresh": tokens["refresh"]}, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_works_before_logout(self, api_client, student_user):
        tokens = self._authorize(api_client, student_user)
        api_client.credentials()

        response = api_client.post(REFRESH, {"refresh": tokens["refresh"]}, format="json")
        assert response.status_code == status.HTTP_200_OK
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")
        assert api_client.get(ME).status_code == status.HTTP_200_OK

    def test_can_login_again_after_logout(self, api_client, student_user):
        self._authorize(api_client, student_user)
        api_client.post(LOGOUT)
        self._authorize(api_client, student_user)
        assert api_client.get(ME).status_code == status.HTTP_200_OK

    def test_logout_requires_login(self, api_client, db):
        assert api_client.post(LOGOUT).status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestRolePermissions:
    def _request(self, user):
        request = APIRequestFactory().get("/")
        request.user = user
        return request

    def test_student_permission(self, student_user, admin_user):
        assert IsStudent().has_permission(self._request(student_user), None)
        assert not IsStudent().has_permission(self._request(admin_user), None)

    def test_admin_permission(self, student_user, admin_user):
        assert IsAdmin().has_permission(self._request(admin_user), None)
        assert not IsAdmin().has_permission(self._request(student_user), None)

    def test_wrong_role_gets_403(self, student_client):
        assert student_client.get("/api/students/").status_code == status.HTTP_403_FORBIDDEN

    def test_me_endpoint(self, student_client):
        response = student_client.get("/api/auth/me/")
        assert response.data["role"] == Role.STUDENT
