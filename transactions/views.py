from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from transactions.pagination import CustomPagination
from transactions.filters import TransactionFilter
from rest_framework import status
from accounts.models import Account
from django.db.models import Sum, Q
import logging

from transactions.models import Transaction
from transactions.serializers import (
    TransactionSerializer, 
    WithdrawalSerializer, 
    DepositSerializer,
    TransactionFilterSerializer,
    TransactionLimitUpgradeRequestSerializer
)

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
            logger.error(f"Transaction processing failed: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
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
        transaction_summary = queryset.aggregate(  
            total_income=Sum('amount', filter=Q(transaction_type='success')),  
            total_expense=Sum('amount', filter=Q(transaction_type='success'))  
        )
        paginator = CustomPagination()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = TransactionFilterSerializer(page, many=True)
            response_data = paginator.get_paginated_response(serializer.data)

            response_data.data['summary'] = transaction_summary  
            return Response(response_data.data, status=status.HTTP_200_OK)
        serializer = TransactionFilterSerializer(queryset, many=True)  
        response_data = {  
            "transactions": serializer.data,  
            "summary": transaction_summary  
        }  
        return Response(response_data, status=status.HTTP_200_OK)
    

class ReversetransactionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, transaction_id):
        try:
            transaction = Transaction.objects.get(id=transaction_id)

            if not request.user.admin:
                return Response({"error": "You do not have permission to reverse this transaction"}, status=status.HTTP_403_FORBIDDEN)
            
            transaction.reverse_transaction()
            return Response({"Message": "Transaction reversed successfully."}, status=status.HTTP_200_OK)
        except Transaction.DoesNotExist:
            return Response({"error": "Transaction not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


class TransactionLimitUpgradeRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = {}
        account = Account.objects.filter(user=request.user).first()
        if not account:
            return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = TransactionLimitUpgradeRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(account=account, user=request.user)  # Pass the account and user explicitly
            data["message"]= "Transaction limit upgrade request submitted successfully."
            data["request_data"] = serializer.data
            # Optionally, you can send an email notification here
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)