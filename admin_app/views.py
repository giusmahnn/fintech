from datetime import datetime
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from accounts.models import User
from accounts.utils import send_email, jwt_auth
from django.template.loader import render_to_string
from admin_app.serializers import CreateAdminSerializer, AdminLoginSerializer
from rbac.models import Role
from django.db import transaction



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