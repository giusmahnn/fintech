from django.urls import path
from rbac.views import (
    ReversetransactionView,
    TransactionLimitUpgradeRequestListView,
    TransactionLimitUpgradeRequestDetailView,
    TransactionLimitUpgradeRequestActionView,
)


urlpatterns = [
    path("reversetransaction/<int:transaction_id>/", ReversetransactionView.as_view(), name="reversetransaction"),
    path('upgrade-requests/', TransactionLimitUpgradeRequestListView.as_view(), name='upgrade-request-list'),
    path('upgrade-requests/<int:request_id>/', TransactionLimitUpgradeRequestDetailView.as_view(), name='upgrade-request-detail'),
    path('upgrade-requests/<int:request_id>/action/', TransactionLimitUpgradeRequestActionView.as_view(), name='upgrade-request-action'),
]
