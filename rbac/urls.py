from django.urls import path
from .views import ManageUsersView


urlpatterns = [
    path('manage-users/', ManageUsersView.as_view(), name='manage_users'),
]