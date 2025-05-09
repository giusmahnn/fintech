from django.contrib import admin
from django.utils.timezone import now
from transactions.models import Transaction, TransactionLimitUpgradeRequest, FlaggedTransaction

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
    list_display = ['account', 'requested_daily_transfer_limit', 'requested_max_single_transfer_amount', 'status', 'action_by']
    exclude = ['created_at', 'updated_at']

    @admin.action(description="Approve selected requests")
    def approve_requests(self, request, queryset):
        for obj in queryset.filter(status='pending'):
            try:
                obj.approve(request.user)
                obj.save()
            except Exception as e:
                self.message_user(request, f"Failed to approve request {obj.id}: {str(e)}", level="error")
        self.message_user(request, "Selected requests have been approved.")

    @admin.action(description="Reject selected requests")
    def reject_requests(self, request, queryset):
        for obj in queryset.filter(status='pending'):
            try:
                obj.reject(request.user)
                obj.save()
            except Exception as e:
                self.message_user(request, f"Failed to reject request {obj.id}: {str(e)}", level="error")
        self.message_user(request, "Selected requests have been rejected.")

    actions = [approve_requests, reject_requests]




@admin.register(FlaggedTransaction)
class FlaggedTransactionAdmin(admin.ModelAdmin):
    list_display = ["transaction", "reason", "flagged_at", "reviewed", "status"]
    actions = ["approve_transactions", "reject_transactions"]

    @admin.action(description="Approve selected transactions")
    def approve_transactions(self, request, queryset):
        for obj in queryset.filter(reviewed=False):
            obj.status = "approved"
            obj.reviewed = True
            obj.reviewed_by = request.user
            obj.reviewed_at = now()
            obj.save()

    @admin.action(description="Reject selected transactions")
    def reject_transactions(self, request, queryset):
        for obj in queryset.filter(reviewed=False):
            obj.status = "rejected"
            obj.reviewed = True
            obj.reviewed_by = request.user
            obj.reviewed_at = now()
            obj.save()