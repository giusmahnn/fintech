from django.contrib import admin
from .models import (
    User,
    Account,
    AccountType,
    # AccountLimit,
    AccountUpgradeRequest
)
# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['get_user', 'email', 'is_verified', 'view_roles']
    search_fields = ['phone_number', 'email']
    list_filter = ['is_verified', 'date_joined', 'last_login']
    ordering = ['date_joined']
    readonly_fields = ['otp_created_at', 'otp']
    
    def view_roles(self, obj):
        return ", ".join([role.name for role in obj.roles.all()])
    
    def get_user(self, obj):
        return obj.get_fullname()
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'currency', 'account_type', 'created_at', 'updated_at']
    search_fields = ['user']
    list_filter = ['account_type', 'created_at', 'updated_at']
    ordering = ['created_at']
    readonly_fields = []
    



@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'interest_rate', 'min_balance', 'max_balance', 'daily_transfer_limit', 'max_single_transfer_amount']
    search_fields = ['name', 'description']
    list_filter = ['name', 'created_at', 'updated_at']
    ordering = ['name']
    fieldsets = (
        ('General Info', {'fields': ('name', 'description')}),
        ('Balance Info', {'fields': ('min_balance', 'max_balance')}),
        ('Transaction Limits', {'fields': ('daily_transfer_limit', 'max_single_transfer_amount')}),
    )



@admin.register(AccountUpgradeRequest)
class AccountUpgradeRequestAdmin(admin.ModelAdmin):
    list_display = ['get_user', 'requested_account_type', 'reason', 'status', 'get_actioned_by']
    search_fields = ['account__user__phone_number', 'status']
    list_filter = ['status', 'created_at']
    ordering = ['created_at']

    def get_user(self, obj):
        return obj.account.user.get_fullname()

    def get_actioned_by(self, obj):
        return obj.get_actioned_by()
    get_actioned_by.short_description = 'Actioned By'

    @admin.action(description="Approve selected requests")
    def approve_requests(self, request, queryset):
        for obj in queryset.filter(status='PENDING'):
            try:
                obj.approve(request.user)
                obj.save()
            except Exception as e:
                self.message_user(request, f"Failed to approve request {obj.id}: {str(e)}", level="error")
        self.message_user(request, "Selected requests have been approved.")

    @admin.action(description="Reject selected requests")
    def reject_requests(self, request, queryset):
        for obj in queryset.filter(status='PENDING'):
            try:
                obj.reject(request.user)
                obj.save()
            except Exception as e:
                self.message_user(request, f"Failed to reject request {obj.id}: {str(e)}", level="error")
        self.message_user(request, "Selected requests have been rejected.")

    actions = [approve_requests, reject_requests]