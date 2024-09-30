from decimal import Decimal

from django.core.exceptions import ValidationError

import pytest
from model_bakery import baker

from accounts.constants import MAX_TRANSFER_AMOUNT_PER_RECIPIENT
from core.services.transfer import Service as TransferService


@pytest.mark.django_db
@pytest.mark.parametrize(
    "amount_to_transfer", [Decimal("0.01"), Decimal("5.55"), Decimal("100.00")]
)
def test_transfer_money_to_one_recipient(amount_to_transfer):
    sender_balance = Decimal("100")
    recipient_balance = Decimal("200")
    sender = baker.make("accounts.User", balance=sender_balance, tin="1111111111")
    recipient = baker.make("accounts.User", balance=recipient_balance, tin="2222222222")

    transfer_service = TransferService(
        sender=sender, amount=amount_to_transfer, recipients=[recipient.tin]
    )
    transfer_service.transfer()

    for obj in [sender, recipient]:
        obj.refresh_from_db()

    assert sender.balance == sender_balance - amount_to_transfer
    assert recipient.balance == recipient_balance + amount_to_transfer


@pytest.mark.django_db
def test_transfer_money_to_multiple_recipients():
    amount_to_transfer = Decimal("60")
    sender_balance = Decimal("100")
    recipient1_balance = Decimal("20")
    recipient2_balance = Decimal("30")

    sender = baker.make("accounts.User", balance=sender_balance, tin="1111111111")
    recipient1 = baker.make(
        "accounts.User", balance=recipient1_balance, tin="2222222222"
    )
    recipient2 = baker.make(
        "accounts.User", balance=recipient2_balance, tin="3333333333"
    )
    recipients = [recipient1, recipient2]

    recipients_tin = [recipient.tin for recipient in recipients]
    transfer_service = TransferService(
        sender=sender, amount=amount_to_transfer, recipients=recipients_tin
    )
    transfer_service.transfer()

    for obj in [sender, recipient1, recipient2]:
        obj.refresh_from_db()

    assert sender.balance == sender_balance - amount_to_transfer

    amount_per_recipient = amount_to_transfer / len(recipients)
    for recipient, balance in zip(recipients, [recipient1_balance, recipient2_balance]):
        assert recipient.balance == balance + amount_per_recipient


@pytest.mark.django_db
def test_transfer_money_when_amount_not_equally_divided():
    amount_to_transfer = Decimal("3.32")
    amount_per_recipient = Decimal("1.10")

    sender_balance = Decimal("100")
    recipient1_balance = Decimal("20")
    recipient2_balance = Decimal("30")
    recipient3_balance = Decimal("40")

    sender = baker.make("accounts.User", balance=sender_balance, tin="1111111111")
    recipient1 = baker.make(
        "accounts.User", balance=recipient1_balance, tin="2222222222"
    )
    recipient2 = baker.make(
        "accounts.User", balance=recipient2_balance, tin="3333333333"
    )
    recipient3 = baker.make(
        "accounts.User", balance=recipient3_balance, tin="444444444444"
    )
    recipients = [recipient1, recipient2, recipient3]

    recipients_tin = [recipient.tin for recipient in recipients]
    transfer_service = TransferService(
        sender=sender, amount=amount_to_transfer, recipients=recipients_tin
    )
    transfer_service.transfer()

    for obj in [sender, *recipients]:
        obj.refresh_from_db()

    remainder = amount_to_transfer - len(recipients) * amount_per_recipient
    assert sender.balance == sender_balance - amount_to_transfer + remainder

    for recipient, balance in zip(
        recipients, [recipient1_balance, recipient2_balance, recipient3_balance]
    ):
        assert recipient.balance == balance + amount_per_recipient


@pytest.mark.django_db
def test_cannot_transfer_money_when_sender_does_not_have_enough_money():
    sender_balance = Decimal("100")
    recipient_balance = Decimal("200")
    sender = baker.make("accounts.User", balance=sender_balance, tin="1111111111")
    recipient = baker.make("accounts.User", balance=recipient_balance, tin="2222222222")

    transfer_service = TransferService(
        sender=sender,
        amount=sender_balance + Decimal("0.01"),
        recipients=[recipient.tin],
    )
    with pytest.raises(ValidationError) as exc_info:
        transfer_service.transfer()

    assert [exc_info.value.message] == ["User doesn't have enough money"]

    for obj in [sender, recipient]:
        obj.refresh_from_db()

    assert sender.balance == sender_balance
    assert recipient.balance == recipient_balance


@pytest.mark.django_db
def test_cannot_transfer_money_when_amount_per_recipient_too_small():
    sender_balance = Decimal("0.01")
    recipient_balance = Decimal("200")
    sender = baker.make("accounts.User", balance=sender_balance, tin="1111111111")
    recipient1 = baker.make(
        "accounts.User", balance=recipient_balance, tin="2222222222"
    )
    recipient2 = baker.make(
        "accounts.User", balance=recipient_balance, tin="333333333333"
    )

    transfer_service = TransferService(
        sender=sender,
        amount=sender_balance,
        recipients=[recipient1.tin, recipient2.tin],
    )
    with pytest.raises(ValidationError) as exc_info:
        transfer_service.transfer()

    assert [exc_info.value.message] == ["The amount is too small"]

    for obj in [sender, recipient1, recipient2]:
        obj.refresh_from_db()

    assert sender.balance == sender_balance
    assert recipient1.balance == recipient_balance
    assert recipient2.balance == recipient_balance


@pytest.mark.django_db
def test_cannot_transfer_money_when_amount_per_recipient_too_big():
    sender_balance = MAX_TRANSFER_AMOUNT_PER_RECIPIENT + Decimal("0.01")
    recipient_balance = Decimal("200")
    sender = baker.make("accounts.User", balance=sender_balance, tin="1111111111")
    recipient1 = baker.make(
        "accounts.User", balance=recipient_balance, tin="2222222222"
    )

    transfer_service = TransferService(
        sender=sender, amount=sender_balance, recipients=[recipient1.tin]
    )
    with pytest.raises(ValidationError) as exc_info:
        transfer_service.transfer()

    assert [exc_info.value.message] == ["The amount per recipient is too big"]

    for obj in [sender, recipient1]:
        obj.refresh_from_db()

    assert sender.balance == sender_balance
    assert recipient1.balance == recipient_balance


@pytest.mark.django_db
def test_cannot_transfer_money_if_tin_not_found():
    sender_balance = Decimal("100")
    sender = baker.make("accounts.User", balance=sender_balance, tin="1111111111")

    tins = ["2222222222", "333333333333"]
    transfer_service = TransferService(
        sender=sender, amount=sender_balance, recipients=tins
    )
    with pytest.raises(ValidationError) as exc_info:
        transfer_service.transfer()

    assert [exc_info.value.message] == ["Tin not found: 2222222222, 333333333333"]

    sender.refresh_from_db()
    assert sender.balance == sender_balance
