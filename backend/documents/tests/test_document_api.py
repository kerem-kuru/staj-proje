from datetime import date
from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from documents.models import Document
from documents.workflow import DocumentStatus

URL = "/api/documents/"


def upload(client, file):
    return client.post(URL, {"file": file}, format="multipart")


@pytest.mark.django_db
class TestStudentUpload:
    def test_valid_document_is_approved_with_report(self, student_client, pdf_file):
        response = upload(student_client, pdf_file("ek16.pdf"))

        assert response.status_code == status.HTTP_201_CREATED, response.data
        assert response.data["status"] == DocumentStatus.APPROVED
        assert response.data["latest_report"]["is_valid"] is True
        assert response.data["extracted_data"]["student_number"] == "220101001"

    def test_missing_info_is_rejected_with_turkish_issues(self, student_client, pdf_file):
        response = upload(student_client, pdf_file("ek16_eksik.pdf"))

        assert response.data["status"] == DocumentStatus.REJECTED
        messages = [issue["message"] for issue in response.data["latest_report"]["issues"]]
        assert "'Staj yeri adı' alanı boş bırakılmış." in messages
        assert response.data["permissions"]["can_reupload"] is True

    def test_reupload_after_fix_gets_approved(self, student_client, pdf_file):
        doc_id = upload(student_client, pdf_file("ek16_eksik.pdf")).data["id"]

        response = student_client.post(f"{URL}{doc_id}/reupload/", {"file": pdf_file("ek16.pdf")}, format="multipart")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == DocumentStatus.APPROVED
        assert response.data["revision"] == 2
        assert len(response.data["reports"]) == 2

    def test_reupload_not_allowed_when_approved(self, student_client, pdf_file):
        doc_id = upload(student_client, pdf_file()).data["id"]
        response = student_client.post(f"{URL}{doc_id}/reupload/", {"file": pdf_file()}, format="multipart")
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_invalid_file_type(self, student_client):
        response = upload(student_client, SimpleUploadedFile("ek16.docx", b"PK..."))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Gönderilen veriler geçersiz."
        assert "file" in response.data["errors"]

    def test_admin_cannot_upload(self, admin_client, pdf_file):
        assert upload(admin_client, pdf_file()).status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestVisibility:
    def test_student_sees_only_own_documents(self, student_client, other_student_user, pdf_file, api_client):
        api_client.force_authenticate(other_student_user)
        other_id = upload(api_client, pdf_file()).data["id"]
        upload(student_client, pdf_file())

        assert student_client.get(URL).data["count"] == 1
        assert student_client.get(f"{URL}{other_id}/").status_code == status.HTTP_404_NOT_FOUND

    def test_admin_sees_all_and_filters_by_status(self, student_client, admin_client, pdf_file):
        upload(student_client, pdf_file("ek16.pdf"))
        upload(student_client, pdf_file("ek16_eksik.pdf"))

        assert admin_client.get(URL).data["count"] == 2
        assert admin_client.get(URL, {"status": DocumentStatus.REJECTED}).data["count"] == 1

    def test_unauthenticated_gets_json_401(self, api_client):
        response = api_client.get(URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response["Content-Type"] == "application/json"


@pytest.mark.django_db
class TestCompletedDocumentRules:
    @pytest.fixture
    def completed_id(self, student_client, admin_client, pdf_file) -> int:
        doc_id = upload(student_client, pdf_file()).data["id"]
        response = admin_client.post(f"{URL}{doc_id}/complete/")
        assert response.data["status"] == DocumentStatus.COMPLETED
        return doc_id

    def test_student_cannot_delete_completed(self, student_client, completed_id):
        response = student_client.delete(f"{URL}{completed_id}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data["detail"] == "Tamamlanan belge öğrenci tarafından değiştirilemez veya silinemez."
        assert Document.objects.filter(pk=completed_id).exists()

    def test_student_cannot_reupload_completed(self, student_client, completed_id, pdf_file):
        response = student_client.post(f"{URL}{completed_id}/reupload/", {"file": pdf_file()}, format="multipart")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_update_and_delete_completed(self, admin_client, completed_id):
        response = admin_client.patch(f"{URL}{completed_id}/", {"admin_note": "Ek-17'ye eklendi."}, format="json")
        assert response.data["admin_note"] == "Ek-17'ye eklendi."

        assert admin_client.delete(f"{URL}{completed_id}/").status_code == status.HTTP_204_NO_CONTENT
        assert not Document.objects.filter(pk=completed_id).exists()

    def test_student_can_delete_unfinished_document(self, student_client, pdf_file):
        doc_id = upload(student_client, pdf_file("ek16_eksik.pdf")).data["id"]
        assert student_client.delete(f"{URL}{doc_id}/").status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestAdminActions:
    def test_reject_requires_note(self, student_client, admin_client, pdf_file):
        doc_id = upload(student_client, pdf_file()).data["id"]
        assert admin_client.post(f"{URL}{doc_id}/reject/", {}).status_code == status.HTTP_400_BAD_REQUEST

        response = admin_client.post(f"{URL}{doc_id}/reject/", {"note": "Kaşe okunmuyor."})
        assert response.data["status"] == DocumentStatus.REJECTED
        assert response.data["admin_note"] == "Kaşe okunmuyor."

    def test_cannot_complete_rejected_document(self, student_client, admin_client, pdf_file):
        doc_id = upload(student_client, pdf_file("ek16_eksik.pdf")).data["id"]
        assert admin_client.post(f"{URL}{doc_id}/complete/").status_code == status.HTTP_409_CONFLICT

    def test_student_cannot_use_admin_actions(self, student_client, pdf_file):
        doc_id = upload(student_client, pdf_file()).data["id"]
        assert student_client.post(f"{URL}{doc_id}/complete/").status_code == status.HTTP_403_FORBIDDEN

    def test_download(self, student_client, pdf_file):
        doc_id = upload(student_client, pdf_file()).data["id"]
        response = student_client.get(f"{URL}{doc_id}/download/")
        assert response.status_code == status.HTTP_200_OK
        assert b"".join(response.streaming_content).startswith(b"%PDF")


@pytest.mark.django_db
class TestWithRealPdfReader:
    """Varsayılan okuyucu (pdf) ile gerçek Ek-16 şablonu üzerinden uçtan uca akış."""

    FIXTURES = Path(__file__).resolve().parents[2] / "readers" / "tests" / "fixtures"

    @pytest.fixture(autouse=True)
    def _pdf_reader(self, settings, monkeypatch):
        settings.DOCUMENT_READER = "pdf"
        monkeypatch.setattr("validation.context.timezone.localdate", lambda: date(2027, 5, 3))

    def _upload_fixture(self, client, name):
        content = (self.FIXTURES / name).read_bytes()
        return upload(client, SimpleUploadedFile(name, content, content_type="application/pdf"))

    def test_blank_form_is_rejected(self, student_client):
        response = self._upload_fixture(student_client, "ek16_bos.pdf")

        assert response.data["status"] == DocumentStatus.REJECTED
        report = response.data["latest_report"]
        assert report["reader_name"] == "pdf"
        assert len(report["issues"]) >= 30

    def test_filled_form_is_approved(self, student_client):
        response = self._upload_fixture(student_client, "ek16_dolu.pdf")

        assert response.data["status"] == DocumentStatus.APPROVED, response.data["latest_report"]
        fields = {f["name"]: f for f in response.data["extracted_fields"]}
        assert fields["company_name"] == {
            "name": "company_name",
            "label": "Staj yeri adı",
            "value": "Örnek Yazılım A.Ş.",
            "unparsed": None,
        }

    def test_non_pdf_content_gets_reader_error_report(self, student_client):
        png = SimpleUploadedFile("ek16.png", b"\x89PNG\r\n\x1a\n0000", content_type="image/png")
        response = upload(student_client, png)

        assert response.data["status"] == DocumentStatus.REJECTED
        [issue] = response.data["latest_report"]["issues"]
        assert issue["code"] == "reader_error"
