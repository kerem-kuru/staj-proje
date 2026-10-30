import pytest

from readers.ek16 import Ek16Data
from validation.context import ValidationContext
from validation.engine import ValidationEngine
from validation.reports import summarize
from validation.types import Severity, ValidationIssue
from validation.validators import BaseValidator, FieldFormatValidator


class AlwaysWarns(BaseValidator):
    code = "always_warns"
    description = "test"

    def validate(self, data: Ek16Data, context: ValidationContext) -> list[ValidationIssue]:
        return [self._issue(None, "uyarı", Severity.WARNING)]


class AlwaysFails(BaseValidator):
    code = "always_fails"
    description = "test"

    def validate(self, data: Ek16Data, context: ValidationContext) -> list[ValidationIssue]:
        return [self._issue("company_name", "hata")]


def test_default_engine_accepts_valid_document(valid_data, context):
    result = ValidationEngine.default().run(valid_data, context)
    assert result.is_valid, result.issues


def test_engine_runs_validators_polymorphically(valid_data, context):
    result = ValidationEngine([AlwaysWarns(), AlwaysFails()]).run(valid_data, context)

    assert [i.code for i in result.issues] == ["always_warns", "always_fails"]
    assert not result.is_valid
    assert summarize(result) == "1 hata ve 1 uyarı bulundu."


def test_warnings_do_not_block_approval(valid_data, context):
    result = ValidationEngine([AlwaysWarns()]).run(valid_data, context)
    assert result.is_valid


def test_result_issues_are_read_only(valid_data, context):
    result = ValidationEngine([AlwaysFails()]).run(valid_data, context)
    assert isinstance(result.issues, tuple)


def test_abstract_validators_cannot_be_instantiated():
    with pytest.raises(TypeError):
        BaseValidator()  # type: ignore[abstract]
    with pytest.raises(TypeError):
        FieldFormatValidator("national_id")  # type: ignore[abstract]
