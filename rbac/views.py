from rbac.permissions import HasPermission
from transactions.models import Transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework.response import Response
from rbac.serializers import TransactionLimitUpgradeRequestSerializer
from transactions.models import TransactionLimitUpgradeRequest

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
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "can_view_upgrade_requests"  # Specify the required permission
    # permission_classes = [AllowAny]  # Allow any user to view the list of requests
    def get(self, request):
        requests = TransactionLimitUpgradeRequest.objects.all()
        serializer = TransactionLimitUpgradeRequestSerializer(requests, many=True)
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
    permission_classes = [IsAuthenticated, HasPermission]
    required_permission = "can_manage_upgrade_requests"  # Specify the required permission
    # permission_classes = [AllowAny]  # Allow any user to approve/reject requests
    def post(self, request, request_id):
        action = request.data.get("action")
        if action not in ["approve", "reject"]:
            return Response({"error": "Invalid action. Use 'approve' or 'reject'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            upgrade_request = TransactionLimitUpgradeRequest.objects.get(id=request_id)
            if action == "approve":
                upgrade_request.approve()
                return Response({"message": "Request approved successfully."}, status=status.HTTP_200_OK)
            elif action == "reject":
                upgrade_request.reject()
                return Response({"message": "Request rejected successfully."}, status=status.HTTP_200_OK)
        except TransactionLimitUpgradeRequest.DoesNotExist:
            return Response({"error": "Request not found."}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)