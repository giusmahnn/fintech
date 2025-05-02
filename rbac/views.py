from rest_framework.views import APIView
from rest_framework.response import Response
from rbac.permissions import HasPermission

class ManageUsersView(APIView):
    permission_classes = [HasPermission]
    required_permission = "can_manage_users"

    def get(self, request):
        return Response({"message": "You have access to manage users."})