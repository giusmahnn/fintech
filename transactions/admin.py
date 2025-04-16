from django.contrib import admin
from .models import Transaction

@admin.action(description="Reverse selected transactions")
def reverse_transactions(modeladmin, request, queryset):
    for transaction in queryset:
        try:
            transaction.reverse_transaction()
        except ValueError as e:
            modeladmin.message_user(request, f"Failed to reverse transaction {transaction.id}: {str(e)}", level="error")

class TransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "transaction_type", "status", "amount", "date")
    actions = [reverse_transactions]

admin.site.register(Transaction, TransactionAdmin)