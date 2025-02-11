from django.urls import path
from .views import (
    home,
    UserCreateView,
    VerifyEmailAddress,
    LoginUsersView,
    ProfileView,
)


urlpatterns = [
    path('', home, name='home'),
    path("signup/", UserCreateView.as_view()),
    path("verify/<str:otp>/", VerifyEmailAddress.as_view()),
    path("login-users/", LoginUsersView.as_view()),
    path("profile/", ProfileView.as_view()),
]