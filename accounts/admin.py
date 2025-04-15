from django.contrib import admin
from .models import (
    User,
    Account,
    AccountType,
    AccountLimit,
    AccountUpgradeRequest
)
# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'email', 'is_verified', 'date_joined', 'last_login']
    search_fields = ['phone_number', 'email']
    list_filter = ['is_verified', 'date_joined', 'last_login']
    ordering = ['date_joined']
    readonly_fields = ['otp_created_at', 'otp']
    # fieldsets = (
    #     (None, {'fields': ('phone_number', 'email', 'password')}),
    #     ('Personal info', {'fields': ('first_name', 'last_name')}),
    #     ('Permissions', {'fields': ('is_verified', 'is_staff', 'is_superuser')}),
    #     ('Important dates', {'fields': ('date_joined')}),
    #     ('OTP', {'fields': ('otp', 'otp_created_at')}),
    #     ('Groups', {'fields': ('groups', 'user_permissions')}),
    # )
@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'currency', 'account_type', 'created_at', 'updated_at']
    search_fields = ['user']
    list_filter = ['account_type', 'created_at', 'updated_at']
    ordering = ['created_at']
    readonly_fields = []
    # fieldsets = (
    #     (None, {'fields': ('user', 'balance', 'currency', 'account_type')}),
    #     ('Important dates', {'fields': ('created_at', 'updated_at')}),
    # )  
@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name', 'description']
    list_filter = ['name']
    ordering = ['name']
    fieldsets = (
        (None, {'fields': ('name', 'description')}),
    )
@admin.register(AccountLimit)
class AccountLimitAdmin(admin.ModelAdmin):
    list_display = ['account_type', 'daily_transfer_limit', 'max_single_transfer_amount']
    search_fields = ['account_type__name']
    list_filter = ['account_type']
    ordering = ['account_type']

    fieldsets = (
        (None, {'fields': ('account_type', 'daily_transfer_limit', 'max_single_transfer_amount')}),
    )
@admin.register(AccountUpgradeRequest)
class AccountUpgradeRequestAdmin(admin.ModelAdmin):
    list_display = ['get_user', 'status', 'created_at']
    search_fields = ['account__user__phone_number', 'status']
    list_filter = ['status', 'created_at']
    ordering = ['created_at']

    fieldsets = (
        (None, {'fields': ('account', 'status')}),
        ('Important dates', {'fields': ('created_at',)}),
    )

    def get_user(self, obj):
        return obj.account.user.phone_number
    get_user.short_description = 'User'
