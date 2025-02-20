from decimal import Decimal
from django.db import models
from accounts.models import Account, User
import uuid
from .choices import TransactionType, Status
# Create your models here.



class Transaction(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(User, related_name="transactions", on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions")
    recipient_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name="received_transactions")
    narration = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default="pending")
    date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.account.user.phone_number} - {self.transaction_type} - {self.status}"
    
    def process_transaction(self):
        amount = Decimal(self.amount)
        if self.transaction_type == "withdrawal":
            if not self.account.can_withdraw(self.amount):
                self.status = "failed"
                self.save()
                raise ValueError("Insufficient balance or below minimum balance")
            self.account.balance -= amount

        elif self.transaction_type == "deposit":
            self.account.balance += self.amount

        elif self.transaction_type == "transfer":
            if not self.recipient_account:
                raise ValueError("Recipient account is required for transfer")
            if not self.account.can_withdraw(amount):
                self.status = "failed"
                self.save()
                raise ValueError("Insufficient balance or below minimum balance")
            self.account.balance -= amount
            self.recipient_account.balance += amount
            self.recipient_account.save()
        self.account.save()
        self.status = "success"
        self.save()

    def recipient_account_name(self):
        return self.recipient_account.user.get_fullname()