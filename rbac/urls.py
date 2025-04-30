from django.urls import path
from rbac.views import (
    ReversetransactionView,
    TransactionLimitUpgradeRequestListView,
    TransactionLimitUpgradeRequestDetailView,
    TransactionLimitUpgradeRequestActionView,
    AccountUpgradeRequestListView,
    AccountUpgradeRequestDetailView,
    AccountUpgradeRequestActionView,
)


urlpatterns = [
    path("reversetransaction/<int:transaction_id>/", ReversetransactionView.as_view(), name="reversetransaction"),
    path('upgrade-requests/', TransactionLimitUpgradeRequestListView.as_view(), name='upgrade-request-list'),
    path('upgrade-requests/<int:request_id>/', TransactionLimitUpgradeRequestDetailView.as_view(), name='upgrade-request-detail'),
    path('upgrade-requests/<int:request_id>/action/', TransactionLimitUpgradeRequestActionView.as_view(), name='upgrade-request-action'),
    path('account-upgrade-requests/', AccountUpgradeRequestListView.as_view(), name='account-upgrade-request-list'),
    path('account-upgrade-requests/<int:request_id>/', AccountUpgradeRequestDetailView.as_view(), name='account-upgrade-request-detail'),
    path('account-upgrade-requests/<int:request_id>/action/', AccountUpgradeRequestActionView.as_view(), name='account-upgrade-request-action'),
]
