from django import forms

from accounts.constants import MIN_TRANSFER_AMOUNT, TIN_MAX_LENGTH, TIN_MIN_LENGTH
from accounts.models import User


class TransferForm(forms.Form):
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

        if not tin_data:
            raise forms.ValidationError(
                f"TIN must be passed through a comma and contain {TIN_MIN_LENGTH} or {TIN_MAX_LENGTH} digits"
            )

        for tin in tins:
            if not tin.isdigit() or not (len(tin) in [TIN_MIN_LENGTH, TIN_MAX_LENGTH]):
                raise forms.ValidationError(
                    f"TIN must be passed through a comma and contain {TIN_MIN_LENGTH} or {TIN_MAX_LENGTH} digits"
                )

        if len(tins) != len(set(tins)):
            raise forms.ValidationError("Tin cannot be repeated")

        return tins

    def clean(self):
        cleaned_data = super().clean()

        recipients = cleaned_data.get("recipients")
        sender = cleaned_data.get("sender")
        if sender and recipients and sender.tin in recipients:
            raise forms.ValidationError("User cannot send money to himself")

        return cleaned_data
