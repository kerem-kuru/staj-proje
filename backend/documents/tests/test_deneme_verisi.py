"""deneme-verisi/ klasöründeki senaryoları gerçek okuyucu ve denetim motorundan geçirir."""
import json
from datetime import date
from pathlib import Path

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from students.models import StudentProfile
from students.services import CsvStudentImporter

DATA = Path(__file__).resolve().parents[3] / "deneme-verisi"
SCENARIOS = json.loads((DATA / "beklenen_sonuclar.json").read_text(encoding="utf-8"))
TODAY = date(2026, 11, 6)  # senaryolar bu tarihe göre üretildi


@pytest.fixture
def dataset(db, settings, monkeypatch):
    settings.DOCUMENT_READER = "pdf"
    monkeypatch.setattr("validation.context.timezone.localdate", lambda: TODAY)
    with (DATA / "ogrenci_veri_seti.csv").open("rb") as stream:
        result = CsvStudentImporter().import_stream(stream)
    assert result.errors == []


def client_for(student_number: str) -> APIClient:
    profile = StudentProfile.objects.get(student_number=student_number)
    profile.user = User.objects.create_user(email=profile.email, password="Gizli.12345")
    profile.save()
    client = APIClient()
    client.force_authenticate(profile.user)
    return client


@pytest.mark.parametrize("scenario", SCENARIOS, ids=[s["file"] for s in SCENARIOS])
def test_scenario(dataset, scenario):
    upload = SimpleUploadedFile(scenario["file"], (DATA / "belgeler" / scenario["file"]).read_bytes())
    payload = {
        "file": upload,
        "plan_start": scenario["plan_start"],
        "plan_end": scenario["plan_end"],
        "plan_weekdays": scenario["plan_weekdays"],
    }

    response = client_for(scenario["student_number"]).post("/api/documents/", payload, format="multipart")

    if scenario["expected"] == "REDDEDILDI":
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        return
    assert response.status_code == status.HTTP_201_CREATED, response.data
    issues = response.data["latest_report"]["issues"]
    errors = {i["code"] for i in issues if i["severity"] == "error"}
    warnings = {i["code"] for i in issues if i["severity"] == "warning"}
    assert response.data["status"] == scenario["expected"], issues
    assert errors == set(scenario["errors"]), issues
    assert warnings == set(scenario["warnings"]), issues
