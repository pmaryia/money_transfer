from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from accounts.forms import TransferForm
from core.services.transfer import Service as TransferService


class TransferMoneyView(FormView):
    template_name = "transfer_money.html"
    form_class = TransferForm
    success_url = reverse_lazy("transfer-success")

    def form_valid(self, form):
        sender = form.cleaned_data["sender"]
        recipients = form.cleaned_data["recipients"]
        amount = form.cleaned_data["amount"]
        try:
            TransferService(sender, amount, recipients).transfer()
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)
        except Exception:
            form.add_error(None, "Unexpected error occurred. Please, try again")
            return self.form_invalid(form)
        return super().form_valid(form)


class TransferSuccessView(TemplateView):
    template_name = "transfer_success.html"
