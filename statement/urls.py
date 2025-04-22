from django.urls import path
from statement.views import AccountStatementView, AccountStatementDownloadView

urlpatterns = [
    path('account-statement/', AccountStatementView.as_view(), name='account_statement'),
    path('account-statement/download/', AccountStatementDownloadView.as_view(), name='account_statement_download'),
]