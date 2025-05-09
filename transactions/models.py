from decimal import Decimal
from django.db import models, transaction
from django.db.models import Sum
from accounts.models import Account, User
from django.utils.timezone import now
import uuid
import logging
from notifications.services import create_notification, send_notification
from transactions.utils import FraudDetection
from .choices import FlaggedStatus, TransactionType, Status, TransactionFlow, UpgradeStatus
# Create your models here.



# Initialize logger
logger = logging.getLogger(__name__)

class Transaction(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    user = models.ForeignKey(User, related_name="transactions", on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="transactions")
    recipient_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name="received_transactions")
    narration = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    transaction_flow = models.CharField(max_length=10, choices=TransactionFlow.choices, default="debit")
    date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.account.user.phone_number} - {self.transaction_type} - {self.transaction_flow} - {self.status}"
    
    

    def process_transaction(self):
        try:
            with transaction.atomic():
                amount = Decimal(self.amount)
                account_type = self.account.account_type

                # Run fraud detection
                fraud_detection = FraudDetection(self)
                fraud_result = fraud_detection.run_checks()
                if fraud_result:
                    self.account.flagged = True
                    self.status = "flagged"
                    self.account.save()
                    logger.warning(f"Transaction {self.id} flagged: {fraud_result}")
                    # Log the flagged transaction
                    FlaggedTransaction.objects.create(
                        transaction=self,
                        reason=fraud_result,
                        flagged_at=now(),
                        status="flagged",
                    )
                    # Notify admins
                    send_notification(
                        user=self.user,
                        message=f"Transaction flagged: {fraud_result}",
                        transaction=self
                    )
                    return
                
                # process the transaction
                if self.transaction_type == "withdrawal":
                    if not self.account.can_withdraw(amount):
                        raise ValueError("Insufficient balance or below minimum balance.")
                    self.account.balance -= amount
                    self.transaction_flow = "debit"

                elif self.transaction_type == "deposit":
                    self.account.balance += amount
                    self.transaction_flow = "credit"

                elif self.transaction_type == "transfer":
                    if not self.recipient_account:
                        raise ValueError("Recipient account is required for transfer.")
                    if not self.account.can_withdraw(amount):
                        self.status = "failed"
                        self.save()
                        raise ValueError("Insufficient balance or below minimum balance.")
                    
                    # Debit the sender's account
                    self.account.balance -= amount
                    self.transaction_flow = "debit"  
                    self.account.save()

                    # Credit the recipient's account   
                    self.recipient_account.balance += amount
                    self.recipient_account.save()

                    # Log the recipient's transaction
                    reciepient_transaction = Transaction.objects.create(
                        user=self.recipient_account.user,
                        account=self.recipient_account,
                        amount=amount,
                        transaction_type="transfer",
                        transaction_flow="credit",
                        status="success",
                    )
                    
                # self.account.save()
                self.status = "success"
                self.save()

                # Create notification
                create_notification(self.user, self)
                if self.transaction_type == "transfer":
                    create_notification(self.recipient_account.user, reciepient_transaction)
                logger.info(f"Transaction {self.id} processed successfully: {self.transaction_type} of {self.amount}")

        except Exception as e:
            logger.error(f"Error processing transaction {self.id}: {e}")
            self.status = "failed"
            self.save()
            raise e

    def recipient_account_name(self):
        return self.recipient_account.user.get_fullname()

    def reverse_transaction(self):
        if self.status != "success":
            raise ValueError("Only successful transactions can be reversed")
        try:
            with transaction.atomic():
                amount = Decimal(str(self.amount))  # Defensive conversion
                if self.transaction_type == "withdrawal":
                    self.account.balance += amount
                    self.account.save()
                elif self.transaction_type == "deposit":
                    self.account.balance -= amount
                    self.account.save()
                elif self.transaction_type == "transfer":
                    if not self.recipient_account:
                        raise ValueError("Recipient account required for transfer reversal")
                    self.recipient_account.balance -= amount
                    self.recipient_account.save()
                    self.account.balance += amount
                    self.account.save()

                self.status = "reversed"
                self.save()

                # Send transaction notification
                # send_transaction_notification(self.user, self)
        except Exception as e:
            logger.error(f"Error reversing transaction {self.id}: {e}")
            raise ValueError(f"Transaction reversal failed: {str(e)}") 
        


class TransactionLimitUpgradeRequest(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="limits_upgrade_requests")
    requested_daily_transfer_limit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    requested_max_single_transfer_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    action_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="actioned_requests", null=True, blank=True)
    status = models.CharField(max_length=10, choices=UpgradeStatus.choices, default=UpgradeStatus.PENDING)
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def approve(self, admin_user):
        if self.status != UpgradeStatus.PENDING:
            raise ValueError("Only pending requests can be approved")
        try:
            with transaction.atomic():
                account = self.account
                # account_type = account.account_type
                account.daily_transfer_limit = self.requested_daily_transfer_limit
                account.max_single_transfer_amount = self.requested_max_single_transfer_amount
                account.save()
                self.action_by = admin_user
                self.status = UpgradeStatus.APPROVED  
                self.save()  
        except Exception as e:
            logger.error(f"Error approving upgrade request {self.account}: {e}")
            raise ValueError(f"Upgrade request approval failed: {str(e)}")

        
    def reject(self, admin_user):
        if self.status != UpgradeStatus.PENDING:
            raise ValueError("Only pending requests can be rejected")
        try:
            with transaction.atomic():
                self.status = UpgradeStatus.REJECTED
                self.action_by = admin_user
                self.save()
                
        except Exception as e:
            logger.error(f"Error rejecting upgrade request {self.account}: {e}")
            raise ValueError(f"Upgrade request rejection failed: {str(e)}")
        


class FlaggedTransaction(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE, related_name="flagged_transaction")
    reason = models.TextField()
    flagged_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_flagged_transactions")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=FlaggedStatus.choices, default=FlaggedStatus.FLAGGED)

    def __str__(self):
        return f"Flagged Transaction {self.transaction.id} - {self.reason} - {self.status}"
    
    def review(self, admin_user, status):
        if self.reviewed:
            raise ValueError("Transaction already reviewed")
        try:
            with transaction.atomic():
                self.reviewed = True
                self.reviewed_by = admin_user
                self.reviewed_at = now()
                self.status = status
                self.save()
                
        except Exception as e:
            logger.error(f"Error reviewing flagged transaction {self.transaction.id}: {e}")
            raise ValueError(f"Flagged transaction review failed: {str(e)}")