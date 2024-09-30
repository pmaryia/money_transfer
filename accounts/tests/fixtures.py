from decimal import Decimal

from django.test import Client

import pytest
from model_bakery import baker


def client():
    return Client()


@pytest.fixture
def sender():
    return baker.make("accounts.User", balance=Decimal("100"), tin="1111111111")


@pytest.fixture
def recipient():
    return baker.make("accounts.User", balance=Decimal("200"), tin="2222222222")
