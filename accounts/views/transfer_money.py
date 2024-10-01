from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from accounts.forms import TransferMoneyForm
from core.services.transfer_money import Service as TransferService


class TransferMoneyView(LoginRequiredMixin, FormView):
    template_name = "transfer_money.html"
    form_class = TransferMoneyForm
    success_url = reverse_lazy("transfer-success")
    login_url = reverse_lazy("login")

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


class TransferMoneySuccessView(TemplateView):
    template_name = "transfer_money_success.html"
