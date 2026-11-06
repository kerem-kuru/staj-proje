import io
from datetime import date

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from students.models import StudentProfile
from students.services import CsvStudentImporter

CSV = (
    "ogrenci_no;ad;soyad;tc_kimlik_no;bolum;sinif;eposta\n"
    "220101001;Ayşe;Yılmaz;10000000146;Bilgisayar Mühendisliği;3;ayse@ogrenci.edu.tr\n"
    "220101002;İsmail;Kaya;;Bilgisayar Mühendisliği;;\n"
    ";Eksik;Satır;;Bilgisayar Mühendisliği;3;\n"
    "220101004;Hatalı;Sınıf;;Bilgisayar Mühendisliği;üç;\n"
)


@pytest.mark.django_db
class TestCsvStudentImporter:
    def test_imports_rows_and_reports_errors(self):
        result = CsvStudentImporter().import_stream(io.BytesIO(CSV.encode("utf-8-sig")))

        assert (result.created, result.updated) == (2, 0)
        assert result.errors == [
            "4. satır: eksik sütun(lar): ogrenci_no",
            "5. satır: 'sinif' sayı olmalı.",
        ]
        assert StudentProfile.objects.get(student_number="220101002").class_year is None

    def test_reimport_updates_existing(self):
        CsvStudentImporter().import_stream(io.BytesIO(CSV.encode()))
        result = CsvStudentImporter().import_stream(io.BytesIO(CSV.replace("Yılmaz", "Kara").encode()))

        assert result.updated == 2
        assert StudentProfile.objects.get(student_number="220101001").last_name == "Kara"

    def test_comma_separated_file(self):
        text = "ogrenci_no,ad,soyad,bolum\n220101009,Ali,Veli,Yazılım Mühendisliği\n"
        result = CsvStudentImporter().import_stream(io.BytesIO(text.encode()))
        assert result.created == 1


FULL_CSV = (
    "ad;soyad;tc_kimlik_no;uyruk;ogrenci_no;dogum_tarihi;ikametgah_adresi;bolum;teslim_yili;"
    "onceki_staj_gun;eposta;telefon;saglik_statusu\n"
    "Elvin;Mammadov;99123456780;Azerbaycan;220101004;15.08.2003;Kuruçeşme Mah., Sahil Cad., No: 3, Daire: 11, "
    "İzmit/Kocaeli;Yazılım Mühendisliği;2026-2027;20;elvin@ogrenci.edu.tr;+90 505 456 78 90;1\n"
    "Tarih;Hatalı;;;220101005;32.13.2003;;Yazılım Mühendisliği;;;;;\n"
    "Gün;Hatalı;;;220101006;;;Yazılım Mühendisliği;;çok;;;\n"
)


@pytest.mark.django_db
class TestDatasetColumns:
    def test_all_columns_from_the_specification_are_saved(self):
        result = CsvStudentImporter().import_stream(io.BytesIO(FULL_CSV.encode("utf-8-sig")))

        assert result.created == 1
        student = StudentProfile.objects.get(student_number="220101004")
        assert student.full_name == "Elvin Mammadov"
        assert student.national_id == "99123456780"
        assert student.nationality == "Azerbaycan"
        assert student.birth_date == date(2003, 8, 15)
        assert student.home_address == "Kuruçeşme Mah., Sahil Cad., No: 3, Daire: 11, İzmit/Kocaeli"
        assert student.submission_year == "2026-2027"
        assert student.previous_internship_days == 20
        assert student.phone == "+90 505 456 78 90"
        assert student.health_status == 1

    def test_bad_values_are_reported_per_row(self):
        result = CsvStudentImporter().import_stream(io.BytesIO(FULL_CSV.encode()))
        assert result.errors == [
            "3. satır: 'dogum_tarihi' GG.AA.YYYY biçiminde tarih olmalı.",
            "4. satır: 'onceki_staj_gun' sayı olmalı.",
        ]


@pytest.mark.django_db
def test_import_endpoint_is_admin_only(admin_client, student_client):
    upload = SimpleUploadedFile("liste.csv", CSV.encode())
    assert student_client.post("/api/students/import/", {"file": upload}).status_code == status.HTTP_403_FORBIDDEN

    upload = SimpleUploadedFile("liste.csv", CSV.encode())
    response = admin_client.post("/api/students/import/", {"file": upload})
    assert response.status_code == status.HTTP_200_OK
    assert response.data["created"] >= 1
