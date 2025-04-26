from django.urls import path
from transactions.views import (
    TransferMoneyView,
    DepositMoneyView,
    WithdrawMoneyView,
    TransactionFilterView,
    ReversetransactionView,
    TransactionLimitUpgradeRequestView,
)






urlpatterns = [
    path('transfer/', TransferMoneyView.as_view()),
    path('deposit/', DepositMoneyView.as_view()),
    path('withdraw/', WithdrawMoneyView.as_view()),  # TODO: Add permission checks for withdrawal amount and account balance.
    path('transaction-filter/', TransactionFilterView.as_view()),
    path('reverse-transaction/', ReversetransactionView.as_view()),
    path('transaction-limit-upgrade-request/', TransactionLimitUpgradeRequestView.as_view()),
]