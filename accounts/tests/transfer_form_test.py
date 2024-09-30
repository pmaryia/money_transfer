from decimal import Decimal

from django.urls import reverse

import pytest
from model_bakery import baker


@pytest.mark.django_db
def test_transfer_money_to_one_recipient(client):
    sender_balance = Decimal("100")
    recipient_balance = Decimal("200")
    sender = baker.make("accounts.User", balance=sender_balance, tin="1111111111")
    recipient = baker.make("accounts.User", balance=recipient_balance, tin="2222222222")

    url = reverse("transfer")
    form_data = {
        "sender": sender.pk,
        "recipients": f"{recipient.tin}",
        "amount": "99.99",
    }

    response = client.post(url, form_data)

    assert response.status_code == 302
    assert response.url == reverse("transfer-success")

    sender.refresh_from_db()
    assert sender.balance == Decimal("0.01")

    recipient.refresh_from_db()
    assert recipient.balance == Decimal("299.99")


@pytest.mark.django_db
def test_transfer_money_to_multiple_recipients(client):
    sender_balance = Decimal("100")
    recipient_balance = Decimal("200")
    sender = baker.make("accounts.User", balance=sender_balance, tin="1111111111")
    recipient = baker.make("accounts.User", balance=recipient_balance, tin="2222222222")

    url = reverse("transfer")
    form_data = {
        "sender": sender.pk,
        "recipients": f"{recipient.tin}",
        "amount": "99.99",
    }

    response = client.post(url, form_data)

    assert response.status_code == 302
    assert response.url == reverse("transfer-success")

    sender.refresh_from_db()
    assert sender.balance == Decimal("0.01")

    recipient.refresh_from_db()
    assert recipient.balance == Decimal("299.99")


@pytest.mark.django_db
def test_transfer_money_when_amount_not_equally_divided(client):
    amount_to_transfer = Decimal("3.32")
    amount_per_recipient = Decimal("1.10")

    sender_balance = Decimal("100")
    recipient1_balance = Decimal("0")
    recipient2_balance = Decimal("20")
    recipient3_balance = Decimal("200")

    sender = baker.make("accounts.User", balance=sender_balance, tin="1111111111")
    recipient1 = baker.make(
        "accounts.User", balance=recipient1_balance, tin="2222222222"
    )
    recipient2 = baker.make(
        "accounts.User", balance=recipient2_balance, tin="333333333333"
    )
    recipient3 = baker.make(
        "accounts.User", balance=recipient3_balance, tin="444444444444"
    )
    recipients = [recipient1, recipient2, recipient3]

    url = reverse("transfer")
    form_data = {
        "sender": sender.pk,
        "recipients": f"{recipient1.tin},{recipient2.tin},{recipient3.tin}",
        "amount": amount_to_transfer,
    }

    response = client.post(url, form_data)

    assert response.status_code == 302
    assert response.url == reverse("transfer-success")

    for obj in [sender, *recipients]:
        obj.refresh_from_db()

    assert sender.balance == sender_balance - amount_per_recipient * len(recipients)

    for recipient, balance in zip(
        recipients, [recipient1_balance, recipient2_balance, recipient3_balance]
    ):
        assert recipient.balance == balance + amount_per_recipient
