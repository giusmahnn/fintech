from django.urls import path
from admin_app.views import (
                            AdminLoginView, 
                            CreateAdminView, 
                            ReversetransactionView, 
                            TransactionLimitUpgradeRequestActionView, 
                            TransactionLimitUpgradeRequestDetailView, 
                            TransactionLimitUpgradeRequestListView,
                            AccountUpgradeRequestListView,
                            AccountUpgradeRequestActionView,
                            AccountUpgradeRequestDetailView,
                            FlaggedAccountListView,
                            FlaggedAccountDetailView,
                            FlaggedAccountActionView,
                            AdminDashboardAnalyticsView
)

urlpatterns = [
    path('admin/login/', AdminLoginView.as_view(), name='admin_login'),
    path('admin/create/', CreateAdminView.as_view(), name='create_admin'),
    path("reversetransaction/<int:transaction_id>/", ReversetransactionView.as_view(), name="reversetransaction"),
    path('upgrade-requests/', TransactionLimitUpgradeRequestListView.as_view(), name='upgrade-request-list'),
    path('upgrade-requests/<int:request_id>/', TransactionLimitUpgradeRequestDetailView.as_view(), name='upgrade-request-detail'),
    path('upgrade-requests/<int:request_id>/action/', TransactionLimitUpgradeRequestActionView.as_view(), name='upgrade-request-action'),
    path('account-upgrade-requests/', AccountUpgradeRequestListView.as_view(), name='account-upgrade-request-list'),
    path('account-upgrade-requests/<int:request_id>/', AccountUpgradeRequestDetailView.as_view(), name='account-upgrade-request-detail'),
    path('account-upgrade-requests/<int:request_id>/action/', AccountUpgradeRequestActionView.as_view(), name='account-upgrade-request-action'),
    path('flagged/', FlaggedAccountListView.as_view(), name='flagged-transactions'),
    path('flagged/<int:request_id>/', FlaggedAccountDetailView.as_view(), name='flagged-transaction-detail'),
    path('flagged/<int:request_id>/review/', FlaggedAccountActionView.as_view(), name='review-flagged'),
    path('dashboard/analytics/', AdminDashboardAnalyticsView.as_view(), name='admin_dashboard_analytics'),
]