from decimal import Decimal

import pytest

from accounts.constants import MAX_RECIPIENTS_COUNT, TIN_MAX_LENGTH, TIN_MIN_LENGTH
from accounts.forms import TransferMoneyForm
from accounts.tests.fixtures import generate_tin


@pytest.mark.django_db
def test_form_is_valid(make_users):
    sender, recipients = make_users(recipients_count=1)

    form_data = {
        "sender": 1,
        "recipients": f"{recipients[0].tin}",
        "amount": Decimal("10"),
    }
    form = TransferMoneyForm(data=form_data)

    assert form.is_valid()


@pytest.mark.django_db
def test_form_is_invalid_when_user_tin_passed_in_recipients(make_users):
    sender, _ = make_users(recipients_count=0)

    form_data = {
        "sender": sender.id,
        "recipients": f"{sender.tin}",
        "amount": Decimal("10"),
    }
    form = TransferMoneyForm(data=form_data)

    assert not form.is_valid()
    assert form.errors["__all__"] == ["User cannot send money to himself"]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "recipients,error_message",
    [
        (" , ", "Ensure this value has at least 10 characters (it has 1)."),
        # recipients passed not through comma
        (
            "1111111111; 2222222222",
            f"TIN must be passed through a comma and contain {TIN_MIN_LENGTH} or {TIN_MAX_LENGTH} digits",
        ),
        # recipients tins have wrong length
        (
            "111111111, 22222222222",
            f"The length of the TIN must be either {TIN_MIN_LENGTH} or {TIN_MAX_LENGTH} digits",
        ),
        # recipients field contain not only digits
        (
            "a123456789",
            f"TIN must be passed through a comma and contain {TIN_MIN_LENGTH} or {TIN_MAX_LENGTH} digits",
        ),
        # recipients tins are repeated
        ("1111111111, 1111111111", "Tin cannot be repeated"),
        # recipients count is more than MAX_RECIPIENTS_COUNT
        (
            ", ".join([f"{generate_tin()}" for i in range(MAX_RECIPIENTS_COUNT + 1)]),
            f"Money cannot be sent to more than {MAX_RECIPIENTS_COUNT} recipients",
        ),
        (
            ",,,,,,,,,,",
            "TIN must be passed through a comma and contain 10 or 12 digits",
        ),
    ],
)
def test_form_is_invalid_when_recipients_format_is_invalid(recipients, error_message):
    form_data = {"sender": 1, "recipients": recipients, "amount": Decimal("10")}
    form = TransferMoneyForm(data=form_data)

    assert not form.is_valid()
    assert form.errors["recipients"] == [error_message]


@pytest.mark.django_db
@pytest.mark.parametrize("amount_to_transfer", [Decimal("0.00"), Decimal("-1.00")])
def test_form_is_invalid_when_transfer_when_invalid_amount_was_passed(
    amount_to_transfer,
):
    form_data = {
        "sender": 1,
        "recipients": f"{generate_tin()}",
        "amount": amount_to_transfer,
    }
    form = TransferMoneyForm(data=form_data)

    assert not form.is_valid()
    assert form.errors["amount"] == [
        "Ensure this value is greater than or equal to 0.01."
    ]
