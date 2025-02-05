from datetime import timezone
from django.shortcuts import render
from rest_framework.views import APIView
from django.conf import settings
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.template.loader import render_to_string
from rest_framework import status
from .utils import *

from .utils import *
from .serializers import *
from .models import *
# Create your views here.


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
            phone_number = serializer.validated_data.get("phone_number")
            password = serializer.validated_data.get("password")
            if phone_number:
                try:
                    user = User.objects.get(phone_number=phone_number)
                except User.DoesNotExist:
                    return Response({"error": "User not found with this phone number."}, status=status.HTTP_404_NOT_FOUND)
            if not user.check_password(password):
                return Response({"error": "Incorrect password."}, status=status.HTTP_401_UNAUTHORIZED)
            context = {
                "name": user.get_fullname(),
                "last_login": user.last_login
            }
            html_message = render_to_string('accounts/login_email.html', context)
            send_email(user.email, 'Login Notification', html_message)
            data['Message'] = 'successfully logged in'
            data["User data"] = UserSerializer(user).data
            data["JWT_Token"] = jwt_auth(user)
            return Response(data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)