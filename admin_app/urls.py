from admin_app.views import AdminLoginView, CreateAdminView
from django.urls import path



urlpatterns = [
    path('admin/login/', AdminLoginView.as_view(), name='admin_login'),
    path('admin/create/', CreateAdminView.as_view(), name='create_admin'),
]