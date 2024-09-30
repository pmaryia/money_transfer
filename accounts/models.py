from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from django.db import models

from accounts.constants import TIN_MAX_LENGTH, ZERO_DECIMAL
from accounts.validators import validate_tin


class User(AbstractUser):
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    # taxpayer identification number
    tin = models.CharField(
        max_length=TIN_MAX_LENGTH, unique=True, validators=[validate_tin]
    )
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=ZERO_DECIMAL,
        validators=[MinValueValidator(ZERO_DECIMAL)],
    )

    REQUIRED_FIELDS = ["first_name", "last_name", "tin"]
