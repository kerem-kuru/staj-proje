from collections.abc import Sequence

from readers.ek16 import Ek16Data

from .context import ValidationContext
from .types import ValidationResult
from .validators import BaseValidator, default_validators


class ValidationEngine:
    """Denetleyicileri sırayla çalıştırır. Hangi alt sınıf olduğunu bilmez, yalnızca `validate()` çağırır."""

    def __init__(self, validators: Sequence[BaseValidator]) -> None:
        self._validators = tuple(validators)

    @classmethod
    def default(cls) -> "ValidationEngine":
        return cls(default_validators())

    def run(self, data: Ek16Data, context: ValidationContext) -> ValidationResult:
        result = ValidationResult()
        for validator in self._validators:
            result.extend(validator.validate(data, context))
        return result
