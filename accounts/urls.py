from django.urls import path

from accounts.views import TransferMoneyView, TransferSuccessView


urlpatterns = [
    path("", TransferMoneyView.as_view(), name="transfer"),
    path("success/", TransferSuccessView.as_view(), name="transfer-success"),
]
