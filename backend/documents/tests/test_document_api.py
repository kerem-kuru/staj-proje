from datetime import date, timedelta
from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from documents.models import Document
from documents.services.internship_plan import InternshipPlan
from documents.workflow import DocumentStatus

URL = "/api/documents/"


def _plan() -> dict:
    today = date.today()
    start = today + timedelta(days=40 + (7 - (today + timedelta(days=40)).weekday()) % 7)
    plan = InternshipPlan.from_work_days(start, 20)
    return {"plan_start": plan.start_date, "plan_end": plan.end_date, "plan_weekdays": [0, 1, 2, 3, 4]}


PLAN = _plan()


def upload(client, file, **overrides):
    return client.post(URL, {**PLAN, "file": file, **overrides}, format="multipart")


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

        response = student_client.post(f"{URL}{doc_id}/reupload/", {**PLAN, "file": pdf_file("ek16.pdf")}, format="multipart")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == DocumentStatus.APPROVED
        assert response.data["revision"] == 2
        assert len(response.data["reports"]) == 2

    def test_reupload_not_allowed_when_approved(self, student_client, pdf_file):
        doc_id = upload(student_client, pdf_file()).data["id"]
        response = student_client.post(f"{URL}{doc_id}/reupload/", {**PLAN, "file": pdf_file()}, format="multipart")
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_invalid_file_type(self, student_client):
        response = upload(student_client, SimpleUploadedFile("ek16.txt", b"metin"))
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Gönderilen veriler geçersiz."
        assert "file" in response.data["errors"]

    @pytest.mark.parametrize(
        ("name", "content"),
        [("ek16.docx", b"PK\x03\x04word"), ("ek16.doc", b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1word")],
    )
    def test_word_files_are_accepted(self, student_client, name, content):
        response = upload(student_client, SimpleUploadedFile(name, content))
        assert response.status_code == status.HTTP_201_CREATED

    def test_word_extension_with_other_content_is_refused(self, student_client):
        response = upload(student_client, SimpleUploadedFile("ek16.docx", b"metin"))
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_plan_is_required(self, student_client, pdf_file):
        response = student_client.post(URL, {"file": pdf_file()}, format="multipart")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert {"plan_start", "plan_end", "plan_weekdays"} <= response.data["errors"].keys()

    def test_plan_end_cannot_precede_start(self, student_client, pdf_file):
        response = upload(student_client, pdf_file(), plan_end=PLAN["plan_start"] - timedelta(days=1))
        assert "plan_end" in response.data["errors"]

    def test_invalid_weekday_is_refused(self, student_client, pdf_file):
        response = upload(student_client, pdf_file(), plan_weekdays=[7])
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_selected_plan_is_saved(self, student_client, pdf_file):
        response = upload(student_client, pdf_file())
        assert response.data["plan_weekdays"] == [0, 1, 2, 3, 4]
        assert response.data["plan_start"] == PLAN["plan_start"].isoformat()

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
        response = student_client.post(f"{URL}{completed_id}/reupload/", {**PLAN, "file": pdf_file()}, format="multipart")
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
        file = SimpleUploadedFile(name, content, content_type="application/pdf")
        return upload(client, file, plan_start=date(2027, 6, 14), plan_end=date(2027, 7, 9))

    def test_blank_form_is_rejected(self, student_client):
        response = self._upload_fixture(student_client, "ek16_bos.pdf")

        assert response.data["status"] == DocumentStatus.REJECTED
        report = response.data["latest_report"]
        assert report["reader_name"] == "pdf"
        assert len(report["issues"]) >= 25

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


@pytest.mark.django_db
class TestEngineerDepartment:
    def _document(self, student_client, pdf_file, engineers):
        doc_id = upload(student_client, pdf_file()).data["id"]
        document = Document.objects.get(pk=doc_id)
        document.extracted_data["engineer_count"] = engineers
        document.save()
        return doc_id

    def test_asked_when_fewer_than_five(self, student_client, pdf_file):
        doc_id = self._document(student_client, pdf_file, 3)
        assert student_client.get(f"{URL}{doc_id}/").data["needs_engineer_department"] is True

    def test_not_asked_for_five_or_more(self, student_client, pdf_file):
        doc_id = self._document(student_client, pdf_file, 5)
        assert student_client.get(f"{URL}{doc_id}/").data["needs_engineer_department"] is False

    def test_student_answers(self, student_client, pdf_file):
        doc_id = self._document(student_client, pdf_file, 3)
        response = student_client.post(
            f"{URL}{doc_id}/engineer-department/", {"engineer_department": "Yazılım Mühendisliği"}, format="json"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["engineer_department"] == "Yazılım Mühendisliği"

    def test_completed_document_is_locked(self, student_client, admin_client, pdf_file):
        doc_id = self._document(student_client, pdf_file, 3)
        admin_client.post(f"{URL}{doc_id}/complete/")
        response = student_client.post(
            f"{URL}{doc_id}/engineer-department/", {"engineer_department": "Yazılım"}, format="json"
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_exclude_status_separates_completed_tab(student_client, admin_client, pdf_file):
    completed = upload(student_client, pdf_file()).data["id"]
    upload(student_client, pdf_file())
    admin_client.post(f"{URL}{completed}/complete/")

    assert admin_client.get(URL, {"exclude_status": "TAMAMLANDI"}).data["count"] == 1
    assert admin_client.get(URL, {"status": "TAMAMLANDI"}).data["count"] == 1
    assert admin_client.get(URL, {"exclude_status": "YOK"}).status_code == status.HTTP_400_BAD_REQUEST
