import pytest

from validation.types import Severity
from validation.validators import EngineerCountValidator


@pytest.mark.parametrize("count", [5, 12])
def test_enough_engineers(valid_data, context, count):
    valid_data.engineer_count = count
    assert EngineerCountValidator().validate(valid_data, context) == []


def test_zero_is_an_error(valid_data, context):
    valid_data.engineer_count = 0
    [issue] = EngineerCountValidator().validate(valid_data, context)
    assert issue.severity is Severity.ERROR


@pytest.mark.parametrize("count", [1, 4])
def test_below_five_asks_for_department(valid_data, context, count):
    valid_data.engineer_count = count
    [issue] = EngineerCountValidator().validate(valid_data, context)
    assert issue.severity is Severity.WARNING
    assert "mezun olduğu bölümü" in issue.message


def test_empty_is_left_to_required_fields(valid_data, context):
    valid_data.engineer_count = None
    assert EngineerCountValidator().validate(valid_data, context) == []
