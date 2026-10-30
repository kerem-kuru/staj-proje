from datetime import date

import pytest

from documents.models import Document
from readers.base import DocumentReader, ReaderError
from readers.ek16 import Ek16Data
from readers.factory import get_document_reader
from readers.mock import MockDocumentReader
from validation.engine import ValidationEngine


@pytest.fixture
def document(student_profile, pdf_file):
    def make(name: str = "ek16.pdf") -> Document:
        return Document.objects.create(student=student_profile, file=pdf_file(name), original_filename=name)

    return make


def test_sample_passes_default_rules(document, context):
    data = MockDocumentReader(today=context.today).read(document())
    assert ValidationEngine.default().run(data, context).is_valid


def test_eksik_scenario(document):
    data = MockDocumentReader().read(document("ek16_eksik.pdf"))
    assert data.company_name is None
    assert data.has_company_stamp is False


def test_preset_is_returned_as_copy(document, valid_data):
    reader = MockDocumentReader(preset=valid_data)
    data = reader.read(document())
    data.company_name = "değişti"
    assert reader.read(document()).company_name == valid_data.company_name


def test_missing_file_raises_reader_error(student_profile):
    with pytest.raises(ReaderError):
        MockDocumentReader().read(Document(student=student_profile))


def test_factory_returns_reader_by_name(settings):
    assert isinstance(get_document_reader("mock"), MockDocumentReader)
    assert isinstance(get_document_reader(), DocumentReader)


def test_ek16_dict_roundtrip(valid_data):
    restored = Ek16Data.from_dict(valid_data.to_dict())
    assert restored == valid_data
    assert isinstance(restored.start_date, date)
