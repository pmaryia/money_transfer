import random
from decimal import Decimal

from django.contrib.auth.hashers import make_password
from django.test import Client

import pytest
from model_bakery import baker

from accounts.constants import TIN_MAX_LENGTH, TIN_MIN_LENGTH


def client():
    return Client()


def generate_tin(number_of_digits=10):
    if number_of_digits not in [TIN_MIN_LENGTH, TIN_MAX_LENGTH]:
        raise ValueError("TIN must be either 10 or 12 digits long")

    return "".join(random.choice("0123456789") for _ in range(number_of_digits))


@pytest.fixture
def make_users():
    def inner(sender_balance=Decimal("100"), recipients_count=1):
        tin = generate_tin()
        sender = baker.make(
            "accounts.User",
            balance=sender_balance,
            tin=tin,
            password=make_password(tin),
        )

        recipients = []
        for i in range(recipients_count):
            tin = generate_tin()
            recipient = baker.make(
                "accounts.User",
                balance=Decimal(str(i * 10)),
                tin=tin,
                password=make_password(tin),
            )
            recipients.append(recipient)
        return sender, recipients

    return inner
