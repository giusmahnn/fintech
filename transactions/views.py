from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from transactions.pagination import CustomPagination
from transactions.filters import TransactionFilter
from rest_framework import status
from accounts.models import Account
import logging

from transactions.models import Transaction
from transactions.serializers import (
    TransactionSerializer, 
    WithdrawalSerializer, 
    DepositSerializer,
    TransactionFilterSerializer)

logger = logging.getLogger("transactions")

class DepositMoneyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        if not amount or Decimal(amount) < 0:
            return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)
        account = get_object_or_404(Account, user=request.user)
        transaction = Transaction.objects.create(
            user=request.user,
            account=account, 
            amount=amount, 
            transaction_type="deposit", 
            status="pending"
            )
        transaction.process_transaction()
        return Response(DepositSerializer(transaction).data, status=status.HTTP_201_CREATED)

class WithdrawMoneyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        if not amount or Decimal(amount) < 0:
            return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)
        account = get_object_or_404(Account, user=request.user)
        transaction = Transaction.objects.create(
            user=request.user,
            account=account, 
            amount=amount, 
            transaction_type="withdrawal", 
            status="pending"
            )
        transaction.process_transaction()

        return Response(WithdrawalSerializer(transaction).data, status=status.HTTP_201_CREATED)

class TransferMoneyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        recipient_account_number = request.data.get('recipient_account_number')
        narration = request.data.get('narration')
        if not amount or Decimal(amount) < 0:
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
            narration=narration,
            transaction_type="transfer",
            status="pending",
        )
        try:
            transaction.process_transaction()
        except Exception as e:
            transaction.status = "completed"
            logger.error(f"Transaction processing failed: {e}")
            transaction.status = "failed"
        transaction.save()
        return Response(TransactionSerializer(transaction).data, status=status.HTTP_201_CREATED)
    


class TransactionFilterView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        queryset = Transaction.objects.filter(user=user)
        transaction_filter = TransactionFilter(request.GET, queryset=queryset)
        if not transaction_filter.is_valid():
            return Response({"error": "Invalid filters"}, status=status.HTTP_400_BAD_REQUEST)
        queryset = transaction_filter.qs
        paginator = CustomPagination()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = TransactionFilterSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)