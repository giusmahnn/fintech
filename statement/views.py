from rest_framework.views import APIView
from rest_framework.response import Response
from django.template.loader import render_to_string
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from fintech.throttling import CustomRateThrottle
from rest_framework.throttling import UserRateThrottle
from weasyprint import HTML
from rest_framework import status
from django.http import HttpResponse
from transactions.models import Transaction
from accounts.models import Account
from accounts.utils import log_audit
from statement.utils import send_statement_email
import datetime
import logging
from transactions.pagination import CustomPagination
from transactions.serializers import TransactionSerializer  # Create a serializer for transactions

logger = logging.getLogger(__name__)

class AccountStatementView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get(self, request):
        user = request.user
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        # Validate query parameters
        if not start_date or not end_date:
            return Response({"error": "start_date and end_date are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            try:
                start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
                end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()
            except ValueError:
                return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)
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
    

class AccountStatementEmailView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [CustomRateThrottle]

    def get(self, request):
        user = request.user
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            return Response({"error": "start_date and end_date are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            start_date = timezone.make_aware(datetime.datetime.strptime(start_date, "%Y-%m-%d"))
            end_date = timezone.make_aware(datetime.datetime.strptime(end_date, "%Y-%m-%d"))
        except ValueError:
            return Response({"error": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        if end_date < start_date:
            return Response({"error": "end_date must be greater than or equal to start_date"}, status=status.HTTP_400_BAD_REQUEST)

        # Get the user's account
        try:
            account = Account.objects.get(user=user)
        except Account.DoesNotExist:
            logger.error(f"Account not found for user {user.email}")
            return Response({"error": "No account found for the authenticated user."}, status=status.HTTP_404_NOT_FOUND)

        # Filter transactions
        transactions = Transaction.objects.filter(
            account=account,
            date__range=[start_date, end_date]
        ).order_by('-date')

        html_string = render_to_string("statement/statement.html", {
            "account": account,
            "transactions": transactions,
            "start_date": start_date,
            "end_date": end_date
        })

        pdf = HTML(string=html_string).write_pdf()

        filename = f"{account.user.get_full_name().replace(' ', '_')}_statement.pdf"
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        # Send email with the statement
        subject = "Your Account Statement"
        # message = "Please find attached your account statement."
        # recipient_list = [account.user.email]
        try:
            send_statement_email(
                user_email=account.user.email,
                subject=subject,
                html_content=html_string,
                pdf_bytes=pdf
            )
            logger.info(f"Account statement emailed to {account.user.email} for the period {start_date} to {end_date}")
            log_audit(
                user=user,
                action="EMAIL_STATEMENT",
                details=f"Account statement emailed to {account.user.email} for the period {start_date} to {end_date}"
            )
        except Exception as e:
            return Response({"error": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"message": "Statement emailed successfully."}, status=status.HTTP_200_OK)
    

class AccountStatementDownloadView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

    def get(self, request):
        user = request.user
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        if not start_date or not end_date:
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=30)
        else:
            start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").date()


        try:
            account = Account.objects.get(user=user)
        except Account.DoesNotExist:
            logger.error(f"Account not found for user {user.email}")
            return Response({"error": "No account found for the authenticated user."}, status=status.HTTP_404_NOT_FOUND)

        transactions = Transaction.objects.filter(
            account=account,
            date__range=[start_date, end_date]
        ).order_by("-date")

        html_string = render_to_string("statement/statement.html", {
            "account": account,
            "transactions": transactions,
            "start_date": start_date,
            "end_date": end_date
        })

        pdf = HTML(string=html_string).write_pdf()

        filename = f"{account.user.get_full_name().replace(' ', '_')}_statement.pdf"
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        # Send email with the statement
        subject = "Your Account Statement"
        # message = "Please find attached your account statement."
        # recipient_list = [account.user.email]
        send_statement_email(
            user_email=account.user.email,
            subject=subject,
            html_content=html_string,
            pdf_bytes=pdf
        )
        logger.info(f"Account statement emailed to {account.user.email} for the period {start_date} to {end_date}")
        log_audit(
            user=user,
            action="EMAIL_STATEMENT",
            details=f"Account statement emailed to {account.user.email} for the period {start_date} to {end_date}"
        )

        return response


# TODO: configure email sending with brevo