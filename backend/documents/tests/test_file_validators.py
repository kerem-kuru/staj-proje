import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from documents.file_validators import FileExtensionTr, FileSignature, MaxFileSize


def make_file(name: str, content: bytes = b"%PDF-1.4") -> SimpleUploadedFile:
    return SimpleUploadedFile(name, content)


class TestFileExtensionTr:
    @pytest.mark.parametrize("name", ["ek16.pdf", "EK16.PDF", "tarama.jpg", "tarama.png"])
    def test_allowed(self, name):
        FileExtensionTr()(make_file(name))

    @pytest.mark.parametrize("name", ["ek16.txt", "ek16", "virus.exe"])
    def test_rejected(self, name):
        with pytest.raises(ValidationError, match="Desteklenmeyen dosya türü"):
            FileExtensionTr()(make_file(name))

    def test_custom_list(self):
        FileExtensionTr(["csv"])(make_file("liste.csv"))
        with pytest.raises(ValidationError):
            FileExtensionTr(["csv"])(make_file("liste.pdf"))


class TestMaxFileSize:
    def test_within_limit(self):
        MaxFileSize(1)(make_file("a.pdf", b"x" * 1024))

    def test_over_limit(self):
        with pytest.raises(ValidationError, match="1 MB'ı aşamaz"):
            MaxFileSize(1)(make_file("a.pdf", b"x" * (1024 * 1024 + 1)))


class TestFileSignature:
    def test_matching_pdf(self):
        FileSignature()(make_file("a.pdf", b"%PDF-1.7 ..."))

    def test_png_renamed_as_pdf(self):
        with pytest.raises(ValidationError, match="uzantısıyla uyuşmuyor"):
            FileSignature()(make_file("a.pdf", b"\x89PNG\r\n\x1a\n...."))

    def test_does_not_move_file_pointer(self):
        file = make_file("a.pdf", b"%PDF-1.7 ...")
        file.seek(3)
        FileSignature()(file)
        assert file.tell() == 3
