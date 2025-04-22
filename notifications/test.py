from django.test import TestCase
from transactions.models import Transaction
from accounts.models import Account, User
from decimal import Decimal
from notifications.utils import send_transaction_notification

class TransactionNotificationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone_number="08070426133",
            email="test@example.com",
            password="password123"
        )
        self.account = Account.objects.create(
            user=self.user,
            balance=Decimal("1000.00"),
            account_number="1234567890"
        )

    def test_send_transaction_notification(self):
        transaction = Transaction.objects.create(
            user=self.user,
            account=self.account,
            amount=Decimal("100.00"),
            transaction_type="deposit",
            status="success"
        )
        send_transaction_notification(self.user, transaction)
        # Check logs or mock email sending to verify the notification was sent