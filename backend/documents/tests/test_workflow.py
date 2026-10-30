import pytest

from documents.exceptions import InvalidStatusTransition
from documents.models import Document
from documents.workflow import DocumentStatus as S
from documents.workflow import DocumentWorkflow


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (S.UPLOADED, S.IN_REVIEW),
        (S.IN_REVIEW, S.REJECTED),
        (S.IN_REVIEW, S.APPROVED),
        (S.REJECTED, S.UPLOADED),
        (S.APPROVED, S.COMPLETED),
        (S.APPROVED, S.REJECTED),
    ],
)
def test_allowed_transitions(current, target):
    assert DocumentWorkflow.can_transition(current, target)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (S.UPLOADED, S.APPROVED),
        (S.REJECTED, S.APPROVED),
        (S.IN_REVIEW, S.COMPLETED),
        (S.COMPLETED, S.UPLOADED),
        (S.COMPLETED, S.REJECTED),
    ],
)
def test_forbidden_transitions(current, target):
    assert not DocumentWorkflow.can_transition(current, target)
    with pytest.raises(InvalidStatusTransition):
        DocumentWorkflow.ensure_transition(current, target)


def test_model_save_rejects_status_jump(student_profile, pdf_file):
    document = Document.objects.create(student=student_profile, file=pdf_file(), original_filename="ek16.pdf")
    document.status = S.COMPLETED  # transition_to kullanmadan doğrudan atama

    with pytest.raises(InvalidStatusTransition):
        document.save()
