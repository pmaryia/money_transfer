import decimal
from typing import List

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404

from accounts.constants import ZERO_DECIMAL
from accounts.models import User


class Service:
    def __init__(self, sender: User, amount: decimal.Decimal, recipients: List[str]):
        self.sender = sender
        self.amount = amount
        self.recipients = recipients
        self.amount_per_recipient = self.calculate_amount_per_recipient()

    def calculate_amount_per_recipient(self) -> decimal.Decimal:
        return (self.amount / len(self.recipients)).quantize(ZERO_DECIMAL)

    def _validate_transfer_amount(self) -> None:
        if self.sender.balance < self.amount:
            raise ValidationError("User doesn't have enough money")

    def _validate_amount_per_recipient(self) -> None:
        if self.amount_per_recipient == ZERO_DECIMAL:
            raise ValidationError("The amount is too small")

    def _validate_recipients(self) -> None:
        accounts = User.objects.filter(tin__in=self.recipients)
        if accounts.count() != len(self.recipients):
            nonexistent_tins = set(self.recipients) - set(
                accounts.values_list("tin", flat=True)
            )
            raise ValidationError(f"Tin not found: {', '.join(nonexistent_tins)}")

    def _validate_transfer(self) -> None:
        self._validate_transfer_amount()
        self._validate_recipients()
        self._validate_amount_per_recipient()

    @transaction.atomic
    def transfer(self) -> None:
        self._validate_transfer()

        accounts = User.objects.filter(tin__in=self.recipients).select_for_update()
        list(accounts)  # cause evaluation, locking the selected rows
        accounts.update(balance=F("balance") + self.amount_per_recipient)

        sender = get_object_or_404(User.objects.select_for_update(), pk=self.sender.pk)
        sender.balance = F("balance") - self.amount_per_recipient * accounts.count()
        sender.save()
