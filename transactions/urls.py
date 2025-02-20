from django.urls import path
from transactions.views import (
    TransferMoneyView
)






urlpatterns = [
    path('transfer/', TransferMoneyView.as_view())
]