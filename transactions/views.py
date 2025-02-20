from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import logging

from transactions.models import Transaction
from transactions.serializers import TransactionSerializer
from accounts.models import Account

logger = logging.getLogger("transactions")

class DepositMoneyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        if not amount or float(amount) < 0:
            return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)
        account = get_object_or_404(Account, user=request.user)
        transaction = Transaction(account=account, amount=float(amount))
        transaction = transaction.deposit(float(amount))
        return Response(TransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)

class WithdrawMoneyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        if not amount or float(amount) < 0:
            return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)
        account = get_object_or_404(Account, user=request.user)
        transaction = Transaction(account=account, amount=float(amount))
        transaction = transaction.withdraw(float(amount))
        return Response(TransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)

class TransferMoneyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        recipient_account_number = request.data.get('recipient_account_number')
        narration = request.data.get('narration')
        if not amount or Decimal(amount) <= 0:
            return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)
        if not recipient_account_number:
            return Response({"error": "Recipient account number is required"}, status=status.HTTP_400_BAD_REQUEST)
        sender_account = get_object_or_404(Account, user=request.user)
        recipient_account = get_object_or_404(Account, account_number=recipient_account_number)
        transaction = Transaction.objects.create(
            user=request.user,
            account=sender_account,
            recipient_account=recipient_account,
            amount=Decimal(amount),
            transaction_type="transfer",
            status="pending",
        )
        transaction.process_transaction()
        return Response(TransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)