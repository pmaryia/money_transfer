from decimal import Decimal
from unittest.mock import patch

from django.urls import reverse

import pytest


@pytest.mark.django_db
@patch("core.services.transfer_money.Service.transfer")
def test_redirect_to_success_page_if_form_and_transfer_was_successful(
    mock_transfer, client, make_users
):
    mock_transfer.return_value = None

    sender, recipients = make_users(recipients_count=3)
    tins = [recipient.tin for recipient in recipients]
    amount_to_transfer = Decimal("33.32")

    form_data = {
        "sender": sender.pk,
        "recipients": ", ".join(tins),
        "amount": amount_to_transfer,
    }
    response = client.post(reverse("transfer"), form_data)

    assert response.status_code == 302
    assert response.url == reverse("transfer-success")


@pytest.mark.django_db
def test_not_redirect_if_form_is_invalid(client, make_users):
    sender, _ = make_users(recipients_count=0)
    sender_balance = sender.balance

    form_data = {
        "sender": sender.pk,
        "recipients": "1a11111111",
        "amount": Decimal("10"),
    }
    response = client.post(reverse("transfer"), form_data)

    assert response.status_code == 200
    assert "transfer_money.html" in [t.name for t in response.templates]
    assert response.context["form"].errors["recipients"] == [
        "TIN must be passed through a comma and contain 10 or 12 digits"
    ]

    sender.refresh_from_db()
    assert sender.balance == sender_balance


@pytest.mark.django_db
def test_not_redirect_if_validation_error_occurred_while_transfer(client, make_users):
    sender, _ = make_users(recipients_count=0)

    form_data = {
        "sender": sender.pk,
        "recipients": "1111111111",
        "amount": Decimal("10"),
    }
    response = client.post(reverse("transfer"), form_data)

    assert response.status_code == 200
    assert "transfer_money.html" in [t.name for t in response.templates]
    assert response.context["form"].errors["__all__"] == ["Tin not found: 1111111111"]
