from decimal import Decimal
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from transactions.pagination import CustomPagination
from transactions.filters import TransactionFilter
from rest_framework import status
from accounts.models import Account
from accounts.utils import log_audit
from django.db.models import Sum, Q
import logging
from notifications.services import send_notification
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
        if transaction.status == 'success':
            log_audit(
                user=request.user,
                action="deposit",
                ip_address=request.META.get('REMOTE_ADDR'),
                metadata={
                    "account_number": account.account_number,
                    "amount": amount,
                    # "transaction_id": transaction.id
                }
            )
        logger.info(f"Deposit successful for account {request.user.email}. Amount: {amount}")
        return Response(DepositSerializer(transaction).data, status=status.HTTP_201_CREATED)

class WithdrawMoneyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        if not amount or Decimal(amount) < 0:
            logger.error(f"Withdrawal failed for account {request.user.email}. Invalid amount: {amount}")
            return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)
        account = get_object_or_404(Account, user=request.user)
        if account.flagged:
            logger.warning(f"Account {account.account_number} flagged for suspicious activity.")
            return Response({"Error": "Please contact support immediately..."}, status=status.HTTP_400_BAD_REQUEST)
        transaction = Transaction.objects.create(
            user=request.user,
            account=account, 
            amount=amount, 
            transaction_type="withdrawal", 
            status="pending"
            )
        transaction.process_transaction()
        if transaction.status == 'success':
            log_audit(
                user=request.user,
                action="withdrawal",
                ip_address=request.META.get('REMOTE_ADDR'),
                metadata={
                    "account_number": account.account_number,
                    "amount": amount,
                    # "transaction_id": transaction.id
                }
            )
        logger.info(f"Withdrawal successful for account {request.user.email}. Amount: {amount}")

        return Response(WithdrawalSerializer(transaction).data, status=status.HTTP_201_CREATED)

class TransferMoneyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount')
        recipient_account_number = request.data.get('recipient_account_number')
        narration = request.data.get('narration')
        if not amount or Decimal(amount) < 0:
            logger.error(f"Transfer failed for account {request.user.email}. Invalid amount: {amount}")
            return Response({"error": "Invalid amount"}, status=status.HTTP_400_BAD_REQUEST)
        if not recipient_account_number:
            logger.error(f"Transfer failed for account {request.user.email}. Recipient account number is required.")
            return Response({"error": "Recipient account number is required"}, status=status.HTTP_400_BAD_REQUEST)
        sender_account = get_object_or_404(Account, user=request.user)
        recipient_account = get_object_or_404(Account, account_number=recipient_account_number)
        if sender_account.flagged:
            logger.warning(f"Sender account {sender_account.account_number} flagged for suspicious activity.")
            return Response({"Error": "Please contact support immediately..."}, status=status.HTTP_400_BAD_REQUEST)
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
            if transaction.status == 'flagged':
                log_audit(
                        user=request.user,
                        action="flagged_transaction",
                        ip_address=request.META.get("REMOTE_ADDR"),
                        metadata={
                            "transaction_id": request.user.id,
                            "reason": "fraud_result"
                        }
                    )
            if transaction.status == 'success':
                log_audit(
                    user=request.user,
                    action="transfer",
                    ip_address=request.META.get('REMOTE_ADDR'),
                    metadata={
                        "account_number": sender_account.account_number,
                        "recipient_account_number": recipient_account.account_number,
                        "amount": amount,
                        # "transaction_id": transaction.id
                    }
                )
                logger.info(f"Transfer successful from {sender_account.account_number} to {recipient_account.account_number}. Amount: {amount}")
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




class TransactionLimitUpgradeRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        serializer = TransactionLimitUpgradeRequestSerializer(data=request.data)
        if serializer.is_valid():
            account = Account.objects.filter(user=request.user).first()
            if not account:
                return Response({"error": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
            serializer.save(account=account)
            send_notification(user=user, 
                              message="Transaction Limit Upgrade Request, Your request has been submitted successfully."
                            )
            logger.info(f"Transaction limit upgrade request submitted by {user.email}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)