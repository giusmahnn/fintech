from django.urls import path
from statement.views import AccountStatementView, AccountStatementEmailView, AccountStatementDownloadView

urlpatterns = [
    path('account-statement/', AccountStatementView.as_view(), name='account_statement'),
    path('account-statement/download/', AccountStatementDownloadView.as_view(), name='account_statement_download'),
    path('account-statement/email/', AccountStatementEmailView.as_view(), name='account_statement_email'),
]