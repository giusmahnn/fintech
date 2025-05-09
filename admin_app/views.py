from datetime import datetime
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from accounts.models import AccountUpgradeRequest, User
from accounts.utils import send_email, jwt_auth
from django.template.loader import render_to_string
from rbac.models import Role
from django.db import transaction
from rbac.permissions import HasPermission
from transactions.models import FlaggedTransaction, Transaction, TransactionLimitUpgradeRequest
from transactions.pagination import CustomPagination
from admin_app.serializers import (
    CreateAdminSerializer, 
    AdminLoginSerializer, 
    TransactionLimitUpgradeRequestSerializer,
    AccountUpgradeRequestSerializer,
    FlaggedTransactionSerializer
)



class CreateAdminView(APIView):
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]

    def post(self, request):
        with transaction.atomic():
            # if not request.user.role == 'admin':
            #     return Response({"error": "You do not have permission to perform this action."}, status=status.HTTP_403_FORBIDDEN)
            serializer = CreateAdminSerializer(data=request.data)
            if serializer.is_valid():
                admin_user = serializer.save()
                admin_role = Role.objects.get(name='Admin')
                admin_user.roles.set([admin_role])
                admin_user.save()
                context = {
                    "name": admin_user.get_fullname(),
                    "verify_link" : f"{settings.BASE_URL}/api/v1/verify/{admin_user.otp}/",
                    "email": admin_user.email,
                    "password": admin_user.password,
                    "current_year": datetime.now().year,
                }
                html_message = render_to_string('admin_app/admin_verify.html', context)
                send_email(admin_user.email, 'Verify Your Email', html_message)
                return Response({"message": f"Admin user {admin_user.get_fullname()} created successfully.",
                                "admin_info":CreateAdminSerializer(admin_user).data,
                                "JWT_Token": jwt_auth(admin_user)}, 
                                status=status.HTTP_201_CREATED
                            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AdminLoginView(APIView):
    """
    View for admin user login.
    """
    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True): 
            user = serializer.validated_data['user']
            print("user:", user)
            context = {
                "name": user.get_fullname(),
                "login_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "current_year": datetime.now().year,
            }
            html_message = render_to_string('admin_app/login_notification.html', context)
            
            # Send login notification email
            send_email(
                user.email,
                'Login Notification',
                html_message
            )
            return Response({
                "message": "Login successful",
                "user_info": AdminLoginSerializer(user).data,
                "JWT_Token": jwt_auth(user)
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    




class ReversetransactionView(APIView):
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "can_reverse_transaction" 

    def get(self, request, transaction_id):
        try:
            transaction = Transaction.objects.get(id=transaction_id)
            return Response({"transaction": transaction.to_dict()}, status=status.HTTP_200_OK)
        except Transaction.DoesNotExist:
            return Response({"error": "Transaction not found."}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, transaction_id):
        try:
            transaction = Transaction.objects.get(id=transaction_id)
            transaction.reverse_transaction()
            return Response({"Message": "Transaction reversed successfully."}, status=status.HTTP_200_OK)
        except Transaction.DoesNotExist:
            return Response({"error": "Transaction not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




class TransactionLimitUpgradeRequestListView(APIView):
    """
    List all transaction limit upgrade requests.
    """
    permission_classes = [HasPermission]
    required_permission = "can_view_upgrade_requests"  # Specify the required permission
    # permission_classes = [AllowAny]  # Allow any user to view the list of requests
    def get(self, request):
        requests = TransactionLimitUpgradeRequest.objects.all().order_by('-created_at')
        paginator = CustomPagination()
        paginated_requests = paginator.paginate_queryset(requests, request)
        serializer = TransactionLimitUpgradeRequestSerializer(paginated_requests, many=True)
        # print("serial", serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransactionLimitUpgradeRequestDetailView(APIView):
    """
    Retrieve a single transaction limit upgrade request by ID.
    """
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "can_view_upgrade_requests"  # Specify the required permission

    def get(self, request, request_id):
        try:
            upgrade_request = TransactionLimitUpgradeRequest.objects.get(id=request_id)
            serializer = TransactionLimitUpgradeRequestSerializer(upgrade_request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except TransactionLimitUpgradeRequest.DoesNotExist:
            return Response({"error": "Request not found."}, status=status.HTTP_404_NOT_FOUND)


class TransactionLimitUpgradeRequestActionView(APIView):
    """
    Approve or reject a transaction limit upgrade request.
    """
    permission_classes = [HasPermission]
    required_permission = "can_approve_limit_upgrade"  # Specify the required permission
    # permission_classes = [AllowAny]  # Allow any user to approve/reject requests
    def post(self, request, request_id):
        action = request.data.get("action")
        user = request.user
        if action not in ["approve", "reject"]:
            return Response({"error": "Invalid action. Use 'approve' or 'reject'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            upgrade_request = TransactionLimitUpgradeRequest.objects.get(id=request_id)
            if action == "approve":
                upgrade_request.approve(user)
                return Response({"message": "Request approved successfully."}, status=status.HTTP_200_OK)
            elif action == "reject":
                upgrade_request.reject(user)
                return Response({"message": "Request rejected successfully."}, status=status.HTTP_200_OK)
        except TransactionLimitUpgradeRequest.DoesNotExist:
            return Response({"error": "Request not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)




class AccountUpgradeRequestListView(APIView):
    """
    List all account upgrade requests.
    """
    permission_classes = [HasPermission]
    required_permission = "can_view_upgrade_requests"  # Specify the required permission
    # permission_classes = [AllowAny]  # Allow any user to view the list of requests
    def get(self, request):
        requests = AccountUpgradeRequest.objects.all().order_by('-created_at')
        paginator = CustomPagination()
        paginated_requests = paginator.paginate_queryset(requests, request)
        serializer = AccountUpgradeRequestSerializer(paginated_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class AccountUpgradeRequestDetailView(APIView):
    """
    Retrieve a single account upgrade request by ID.
    """
    permission_classes = [HasPermission]
    required_permission = "can_view_upgrade_requests"  # Specify the required permission

    def get(self, request, request_id):
        try:
            upgrade_request = AccountUpgradeRequest.objects.get(id=request_id)
            serializer = AccountUpgradeRequestSerializer(upgrade_request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except AccountUpgradeRequest.DoesNotExist:
            return Response({"error": "Request not found."}, status=status.HTTP_404_NOT_FOUND)
        


class AccountUpgradeRequestActionView(APIView):
    permission_classes = [HasPermission]
    required_permission = "can_approve_limit_upgrade"

    def post(self, request, request_id):
        action = request.data.get("action")
        user = request.user
        if action not in ["approve", "reject"]:
            return Response({"error": "Invalid action. Use 'approve' or 'reject'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            upgrade_request = AccountUpgradeRequest.objects.get(id=request_id)
            if action == "approve":
                upgrade_request.approve(user)
                # Send email notification to the user
                return Response({"message": "Request approved successfully."}, status=status.HTTP_200_OK)
            elif action == "reject":
                upgrade_request.reject(user)
                return Response({"message": "Request rejected successfully."}, status=status.HTTP_200_OK)
        except AccountUpgradeRequest.DoesNotExist:
            return Response({"error": "Request not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class FlaggedAccountListView(APIView):
    """
    List all account upgrade requests.
    """
    permission_classes = [HasPermission]
    required_permission = "can_view_upgrade_requests"  # Specify the required permission
    # permission_classes = [AllowAny]  # Allow any user to view the list of requests
    def get(self, request):
        requests = FlaggedTransaction.objects.all().order_by('-flagged_at')
        paginator = CustomPagination()
        paginated_requests = paginator.paginate_queryset(requests, request)
        serializer = FlaggedTransactionSerializer(paginated_requests, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class FlaggedAccountDetailView(APIView):
    """
    Retrieve a single account upgrade request by ID.
    """
    permission_classes = [HasPermission]
    required_permission = "can_view_upgrade_requests"  # Specify the required permission

    def get(self, request, request_id):
        try:
            upgrade_request = FlaggedTransaction.objects.get(id=request_id)
            serializer = FlaggedTransactionSerializer(upgrade_request)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except FlaggedTransaction.DoesNotExist:
            return Response({"error": "Request not found."}, status=status.HTTP_404_NOT_FOUND)



class FlaggedAccountActionView(APIView):
    permission_classes = [HasPermission]
    required_permission = "can_approve_limit_upgrade"

    def post(self, request, request_id):
        status_value = request.data.get("status_value")
        if status_value not in ["unflagged", "rejected"]:
            return Response({"error": "Invalid status value. Use 'approved' or 'rejected'."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            flagged = FlaggedTransaction.objects.get(id=request_id)
            flagged.review(request.user, status_value)
            if status_value == "unflagged":
                flagged.transaction.account.flagged = False
                flagged.transaction.account.save()
                
            return Response({"message": "Flagged transaction reviewed successfully."}, status=status.HTTP_200_OK)
        except FlaggedTransaction.DoesNotExist:
            return Response({"error": "Flagged transaction not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)