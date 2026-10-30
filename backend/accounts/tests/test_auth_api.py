import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory

from accounts.models import Role
from accounts.permissions import IsAdmin, IsStudent

REGISTER = "/api/auth/register/"
LOGIN = "/api/auth/login/"

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

    def test_me_endpoint(self, student_client):
        response = student_client.get("/api/auth/me/")
        assert response.data["role"] == Role.STUDENT
