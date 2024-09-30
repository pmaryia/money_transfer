from django import forms

from accounts.constants import MAX_RECIPIENTS_COUNT, MIN_TRANSFER_AMOUNT, TIN_MAX_LENGTH, TIN_MIN_LENGTH
from accounts.models import User
from accounts.validators import validate_tin


class TransferMoneyForm(forms.Form):
    sender = forms.ModelChoiceField(queryset=User.objects.all())
    recipients = forms.CharField(
        label="Recipients tin",
        strip=True,
        min_length=TIN_MIN_LENGTH,
        widget=forms.Textarea(attrs={"placeholder": "Enter TIN separated by commas"}),
    )
    amount = forms.DecimalField(
        max_digits=10, decimal_places=2, min_value=MIN_TRANSFER_AMOUNT
    )

    def clean_recipients(self):
        tin_data = self.cleaned_data["recipients"]
        tins = [inn.strip() for inn in tin_data.split(",") if inn.strip()]

        if not tins:
            raise forms.ValidationError(
                f"TIN must be passed through a comma and contain {TIN_MIN_LENGTH} or {TIN_MAX_LENGTH} digits"
            )

        for tin in tins:
            validate_tin(tin)

        tins_count = len(tins)
        if tins_count != len(set(tins)):
            raise forms.ValidationError("Tin cannot be repeated")

        if tins_count > MAX_RECIPIENTS_COUNT:
            raise forms.ValidationError(
                f"Money cannot be sent to more than {MAX_RECIPIENTS_COUNT} recipients"
            )

        return tins

    def clean(self):
        cleaned_data = super().clean()

        recipients = cleaned_data.get("recipients")
        sender = cleaned_data.get("sender")
        if sender and recipients and sender.tin in recipients:
            raise forms.ValidationError("User cannot send money to himself")

        return cleaned_data
