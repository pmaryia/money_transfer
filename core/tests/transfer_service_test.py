from decimal import Decimal

from django.core.exceptions import ValidationError

import pytest

from accounts.constants import MAX_TRANSFER_AMOUNT_PER_RECIPIENT
from core.services.transfer_money import Service as TransferService


@pytest.mark.django_db
@pytest.mark.parametrize(
    "amount_to_transfer", [Decimal("0.01"), Decimal("5.55"), Decimal("100")]
)
def test_transfer_money_to_one_recipient(amount_to_transfer, make_users):
    sender, recipients = make_users()
    recipient = recipients[0]

    sender_balance = sender.balance
    recipient_balance = recipient.balance

    transfer_service = TransferService(
        sender=sender, amount=amount_to_transfer, recipients=[recipient.tin]
    )
    transfer_service.transfer()

    for obj in [sender, *recipients]:
        obj.refresh_from_db()

    assert sender.balance == sender_balance - amount_to_transfer
    assert recipient.balance == recipient_balance + amount_to_transfer


@pytest.mark.django_db
@pytest.mark.parametrize(
    "amount_to_transfer,amount_per_recipient",
    [
        (Decimal("33.33"), Decimal("11.11")),
        (Decimal("33.32"), Decimal("11.10")),
    ],
    ids=["amount_equally_divided", "amount_not_equally_divided"],
)
def test_transfer_money_to_multiple_recipients(
    make_users, amount_to_transfer, amount_per_recipient
):
    sender, recipients = make_users(recipients_count=3)
    recipient1, recipient2, recipient3 = recipients

    sender_balance = sender.balance
    recipient1_balance, recipient2_balance, recipient3_balance = (
        recipient1.balance,
        recipient2.balance,
        recipient3.balance,
    )

    transfer_service = TransferService(
        sender=sender,
        amount=amount_to_transfer,
        recipients=[recipient.tin for recipient in recipients],
    )
    transfer_service.transfer()

    for obj in [sender, *recipients]:
        obj.refresh_from_db()

    assert sender.balance == sender_balance - len(recipients) * amount_per_recipient

    for recipient, balance in zip(
        recipients, [recipient1_balance, recipient2_balance, recipient3_balance]
    ):
        assert recipient.balance == balance + amount_per_recipient


@pytest.mark.django_db
@pytest.mark.parametrize(
    "sender_balance,amount_to_transfer,error_message",
    [
        (Decimal("10"), Decimal("10.01"), "User doesn't have enough money"),
        (Decimal("0.01"), Decimal("0.01"), "The amount is too small"),
        (
            MAX_TRANSFER_AMOUNT_PER_RECIPIENT * 3,
            MAX_TRANSFER_AMOUNT_PER_RECIPIENT * 3,
            "The amount per recipient is too big",
        ),
    ],
    ids=[
        "user_does_not_have_enough_money",
        "transfer_amount_too_small",
        "amount_per_recipient_too_big",
    ],
)
def test_cannot_transfer_money_because_of_invalid_amount(
    sender_balance, amount_to_transfer, error_message, make_users
):
    sender, recipients = make_users(sender_balance=sender_balance, recipients_count=2)

    recipient1, recipient2 = recipients
    recipient1_balance, recipient2_balance = recipient1.balance, recipient2.balance

    transfer_service = TransferService(
        sender=sender,
        amount=amount_to_transfer,
        recipients=[recipient1.tin, recipient2.tin],
    )
    with pytest.raises(ValidationError) as exc_info:
        transfer_service.transfer()

    assert [exc_info.value.message] == [error_message]

    for obj in [sender, *recipients]:
        obj.refresh_from_db()

    assert sender.balance == sender_balance
    assert recipient1.balance == recipient1_balance
    assert recipient2.balance == recipient2_balance


@pytest.mark.django_db
def test_cannot_transfer_money_if_tin_not_found(make_users):
    sender, _ = make_users()
    sender_balance = sender.balance

    transfer_service = TransferService(
        sender=sender, amount=sender_balance, recipients=["2222222222", "333333333333"]
    )
    with pytest.raises(ValidationError) as exc_info:
        transfer_service.transfer()

    assert [exc_info.value.message] == ["Tin not found: 2222222222, 333333333333"]

    sender.refresh_from_db()
    assert sender.balance == sender_balance


@pytest.mark.django_db
def test_cannot_transfer_money_if_user_does_not_exist(make_users):
    sender, recipients = make_users()
    sender.delete()

    recipient = recipients[0]
    recipient_balance = recipient.balance

    transfer_service = TransferService(
        sender=sender, amount=Decimal("10.00"), recipients=[recipient.tin]
    )
    with pytest.raises(ValidationError) as exc_info:
        transfer_service.transfer()

    assert [exc_info.value.message] == ["Sender does not exist"]
    assert recipient.balance == recipient_balance
