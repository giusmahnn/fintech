from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.http import HttpResponse
from transactions.models import Transaction
from accounts.models import Account
from statement.utils import generate_pdf_statement
import datetime



from rest_framework.pagination import PageNumberPagination
from transactions.pagination import CustomPagination
from transactions.serializers import TransactionSerializer  # Create a serializer for transactions

class AccountStatementView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Validate query parameters
        if not start_date or not end_date:
            return Response({"error": "start_date and end_date are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
        
        if end_date < start_date:
            return Response({"error": "end_date must be greater than or equal to start_date"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the user's account
        try:
            account = Account.objects.get(user=user)
        except Account.DoesNotExist:
            return Response({"error": "No account found for the authenticated user."}, status=status.HTTP_404_NOT_FOUND)

        # Filter transactions
        transactions = Transaction.objects.filter(
            account=account,
            date__range=[start_date, end_date]
        ).order_by('-date')

        # Apply pagination
        paginator = CustomPagination()
        paginated_transactions = paginator.paginate_queryset(transactions, request)
        serialized_transactions = TransactionSerializer(paginated_transactions, many=True)

        # Return paginated response
        return paginator.get_paginated_response(serialized_transactions.data)
    


class AccountStatementDownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Validate query parameters
        if not start_date or not end_date:
            return Response(
                {"error": "Both 'start_date' and 'end_date' query parameters are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"error": "Invalid date format. Use 'YYYY-MM-DD'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if end_date < start_date:
            return Response(
                {"error": "'end_date' cannot be earlier than 'start_date'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get the user's account
        try:
            account = Account.objects.get(user=user)
        except Account.DoesNotExist:
            return Response(
                {"error": "No account found for the authenticated user."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Filter transactions for the user's account within the date range
        transactions = Transaction.objects.filter(
            account=account,
            date__range=[start_date, end_date],
        ).order_by('date')

        # Generate the PDF
        response = generate_pdf_statement(account, transactions, start_date, end_date)
        return response


# TODO: Email the statement to the user