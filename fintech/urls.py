"""
URL configuration for fintech project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import permissions  
from drf_yasg.views import get_schema_view  
from drf_yasg import openapi  
from django.urls import path 



schema_view = get_schema_view(  
   openapi.Info(  
      title="Your API Title",  
      default_version='v1',  
      description="Test description",  
      terms_of_service="https://www.yourtermsofservice.com/",  
      contact=openapi.Contact(email="contact@yourapi.local"),  
      license=openapi.License(name="BSD License"),  
   ),  
   public=True,  
   permission_classes=(permissions.AllowAny,),  
)  

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('admin/', admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    path('api/v1/accounts/', include('accounts.urls')),
    path('api/v1/transactions/', include('transactions.urls')),
    path('api/v1/notifications/', include('notifications.urls')),
    path('api/v1/statement/', include('statement.urls')),
    path('api/v1/rbac/', include('rbac.urls')),
    path('api/v1/admin-space/', include('admin_app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)