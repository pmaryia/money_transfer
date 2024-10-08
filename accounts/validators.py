from django.core.exceptions import ValidationError

from accounts.constants import TIN_MAX_LENGTH, TIN_MIN_LENGTH


def validate_tin(value):
    if not value.isdigit():
        raise ValidationError(
            f"TIN must be passed through a comma and contain {TIN_MIN_LENGTH} or {TIN_MAX_LENGTH} digits"
        )

    if len(value) not in [TIN_MIN_LENGTH, TIN_MAX_LENGTH]:
        raise ValidationError(
            f"The length of the TIN must be either {TIN_MIN_LENGTH} or {TIN_MAX_LENGTH} digits"
        )
