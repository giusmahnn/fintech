from django.urls import path
from .views import (
    home,
    UserCreateView,
    VerifyEmailAddress
)


urlpatterns = [
    path('', home, name='home'),
    path("signup/", UserCreateView.as_view()),
    path("verify/<str:otp>/", VerifyEmailAddress.as_view())
    
]