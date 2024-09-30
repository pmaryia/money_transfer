from django.urls import path

from accounts.views.transfer_money import TransferMoneySuccessView, TransferMoneyView


urlpatterns = [
    path("", TransferMoneyView.as_view(), name="transfer"),
    path("success/", TransferMoneySuccessView.as_view(), name="transfer-success"),
]
