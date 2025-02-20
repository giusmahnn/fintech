from django.urls import path
from transactions.views import (
    TransferMoneyView,
    DepositMoneyView,
    WithdrawMoneyView
)






urlpatterns = [
    path('transfer/', TransferMoneyView.as_view()),
    path('deposit/', DepositMoneyView.as_view()),
    path('withdraw/', WithdrawMoneyView.as_view()),  # TODO: Add permission checks for withdrawal amount and account balance.
]