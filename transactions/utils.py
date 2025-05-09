from decimal import Decimal
from django.utils.timezone import now
from django.db.models import Sum, Avg
import logging

logger = logging.getLogger("transactions")


class FraudDetection:
    """
    A class to detect fraudulent transactions based on certain criteria.
    """

    def __init__(self, transaction):
        self.transaction = transaction

    def check_limits(self):
        account_type = self.transaction.account.account_type
        if self.transaction.amount > account_type.max_single_transfer_amount:
            logger.warning(f"Transaction amount {self.transaction.amount} exceeds the maximum single transfer limit.")
            return "Transaction exceeds maximum single transfer limit."
        
        # Check daily transfer limit
        today = now().date()
        daily_total = self.transaction.account.transactions.filter(
            date__date=today
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal(0)

        if daily_total + self.transaction.amount > account_type.daily_transfer_limit:
            logger.warning(f"Transaction amount {self.transaction.amount} exceeds the daily transfer limit.")
            return "Transaction exceeds daily transfer limit."
        return None

    def check_behaviour(self):
        """Check for unusual transaction patterns."""
        average_transaction = self.transaction.account.transactions.aggregate(
            Avg('amount')
        )['amount__avg'] or Decimal(0)
        if self.transaction.amount > average_transaction * 10:
            logger.warning(f"Transaction amount {self.transaction.amount} is unusually high compared to average.")
            return "Unusual transaction pattern detected."
        return None

    def run_checks(self):
        """
        Run all fraud detection checks.
        """
        checks = [
            self.check_limits,
            self.check_behaviour
        ]
        for check in checks:
            result = check()
            if result:
                return result
        return None