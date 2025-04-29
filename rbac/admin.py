from django.contrib import admin
from .models import Role, Permission

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ["name"]
    filter_horizontal = ["permissions"]

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ["name", "description"]