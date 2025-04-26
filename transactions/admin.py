from django.contrib import admin
from transactions.models import Transaction, TransactionLimitUpgradeRequest

@admin.action(description="Reverse selected transactions")
def reverse_transactions(modeladmin, request, queryset):
    for transaction in queryset:
        try:
            transaction.reverse_transaction()
        except ValueError as e:
            modeladmin.message_user(request, f"Failed to reverse transaction {transaction.id}: {str(e)}", level="error")

class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "transaction_type", "transaction_flow", "status", "amount", "date")
    actions = [reverse_transactions]

admin.site.register(Transaction, TransactionAdmin)


@admin.register(TransactionLimitUpgradeRequest)
class TransactionLimitUpgradeRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'account', 'requested_daily_transfer_limit', 'requested_max_single_transfer_amount', 'status']
    exclude = ['created_at', 'updated_at']
    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        for obj in queryset.filter(status='PENDING'):
            obj.approve()
        self.message_user(request, "Selected requests have been approved.")

    def reject_requests(self, request, queryset):
        for obj in queryset.filter(status='PENDING'):
            obj.reject()
        self.message_user(request, "Selected requests have been rejected.")
