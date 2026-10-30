from datetime import date

from validation.types import Severity
from validation.validators import HealthStatusValidator, InternshipConditionsValidator
from validation.validators.declarations import age_on


def test_age_on_birthday_boundary():
    assert age_on(date(2002, 6, 14), date(2027, 6, 13)) == 24
    assert age_on(date(2002, 6, 14), date(2027, 6, 14)) == 25


class TestHealthStatusValidator:
    def test_under_25_any_option(self, valid_data, context):
        assert HealthStatusValidator().validate(valid_data, context) == []

    def test_25_or_older_without_option_6_is_warned(self, valid_data, context):
        valid_data.birth_date = date(2001, 1, 1)
        [issue] = HealthStatusValidator().validate(valid_data, context)
        assert issue.severity is Severity.WARNING
        assert "26 yaşında" in issue.message

    def test_25_or_older_with_option_6(self, valid_data, context):
        valid_data.birth_date = date(2001, 1, 1)
        valid_data.health_status = 6
        assert HealthStatusValidator().validate(valid_data, context) == []

    def test_birth_date_in_future(self, valid_data, context):
        valid_data.birth_date = date(2030, 1, 1)
        [issue] = HealthStatusValidator().validate(valid_data, context)
        assert issue.field == "birth_date"


class TestInternshipConditionsValidator:
    def test_domestic_unpaid_has_no_notes(self, valid_data, context):
        assert InternshipConditionsValidator().validate(valid_data, context) == []

    def test_abroad_and_paid_are_warnings(self, valid_data, context):
        valid_data.is_abroad = True
        valid_data.is_paid = True

        issues = InternshipConditionsValidator().validate(valid_data, context)

        assert [i.field for i in issues] == ["is_abroad", "is_paid"]
        assert all(i.severity is Severity.WARNING for i in issues)
        assert "EK-18" in issues[1].message
