from django.shortcuts import render
from django.urls import reverse
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.template.loader import render_to_string
from drf_yasg.utils import swagger_auto_schema  
from drf_yasg import openapi 
from rest_framework import status
import logging
from .utils import (
    generate_otp,
    send_email,
    jwt_auth,
)
from .models import Account, User
from .serializers import (
    UserSerializer,
    LoginSerializer,
    ProfileSerializer,
    ResetPasswordSerializer
)
# Create your views here.

logger = logging.getLogger("accounts")

def home(request):
    context = {}  # Add context variables here if needed
    return render(request, 'accounts/home.html', context)


class UserCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = {}
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.otp = generate_otp()
            user.otp_created()
            user.save()
            context = {
                "name": user.get_fullname(),
                "verify_link" : f"{settings.BASE_URL}/api/v1/verify/{user.otp}/",
            }
            html_message = render_to_string('accounts/verify_email.html', context)
            send_email(user.email, 'Verify Your Email', html_message)
            data['Message'] = 'successfully registered a new user'
            data["User data"] = UserSerializer(user).data
            data["JWT_Token"] = jwt_auth(user)
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class VerifyEmailAddress(APIView):
    def get(self, request, otp):
        if not otp:
            return Response({"message":"OTP is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(otp=otp)
            user.is_verified = True
            user.reset_otp()
            user.save()
            return Response({"Message": "Your email has been verified"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"Message": "Invalid OTP"})



class LoginUsersView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = {}
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            context = {
                "name": user.get_fullname(),
                "last_login": user.last_login,
            }
            html_message = render_to_string('accounts/login_email.html', context)
            send_email(user.email, 'Login Notification', html_message)
            data['Message'] = 'successfully logged in'
            data["User data"] = UserSerializer(user).data
            data["JWT_Token"] = jwt_auth(user)
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        account = Account.objects.get(user=user)
        serializer = ProfileSerializer(account)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        account = Account.objects.filter(user=request.user).first()
        if not account:
            return Response({"message": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProfileSerializer(account, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"User {request.user.email} accessed their profile.")
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class InitializePasswordView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_summary="Send OTP to reset password",
        operation_description="This endpoint sends an OTP to the user's email address to initiate the password reset process.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email address of the user'),
            },
            required=['email'],
        ),
        responses={
            200: 'OTP sent successfully',
            400: 'Email is required',
            404: 'User not found',
        },
    )

    def post(self, request):
        data = {}
        email = request.data.get("email")
        if not email:
            logger.error("Email is required")
            return Response({"message":"Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(email=email)
            user.otp = generate_otp()
            user.otp_created()
            user.save()
            context = {
                "name": user.get_fullname(),
                "reset_link" : f"{settings.BASE_URL}/api/v1/reset-password/{user.otp}/",
            }
            html_message = render_to_string('accounts/rest_password.html', context)
            send_email(user.email, 'Reset Your Password', html_message)
            data['Message'] = 'successfully sent otp to reset password'
            logger.info(f'reset password otp sent to {email}')
            return Response(data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            logger.error("User not found")
            return Response({"message":"User not found"}, status=status.HTTP_404_NOT_FOUND)
        


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]
    @swagger_auto_schema(
        operation_summary="Reset password",
        operation_description="This endpoint resets the password for the user identified by the provided OTP.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'otp': openapi.Schema(type=openapi.TYPE_STRING, description='OTP for password reset'),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New password'),
            },
            required=['otp', 'new_password'],
            example={
                'otp': '123456',
                'new_password': 'NewPassword123',
            },
        ),
        responses={
            200: 'Password reset successfully',
            400: 'OTP or password is required',
            404: 'User not found',
            403: 'Incorrect OTP',
        },
    )

    def post(self, request, otp):
        serializer = ResetPasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            data = serializer.validated_data
            try:
                user = User.objects.get(otp=otp)
            except User.DoesNotExist:
                logger.error(f"Password reset failed: No user found for OTP {otp}")
                return Response({"error": "Invalid OTP or user not found."}, status=status.HTTP_404_NOT_FOUND)

            user.set_password(data["password"])
            user.reset_otp()
            user.save()

            context = {
                "name": user.get_fullname(),
            }
            html_message = render_to_string("accounts/password_reset_email.html", context)
            send_email(user.email, "Password Reset Successful", html_message)

            logger.info(f"Password reset successful for {user.email}")
            return Response({"message": "Successfully reset password"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
