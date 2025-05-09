from django.core.mail import send_mail
from django.conf import settings
import logging

from accounts.models import User

logger = logging.getLogger(__name__)

def send_fraud_alert(transaction, reason):
    """
    Notify admins about a flagged transaction.
    """
    try:
        subject = f"Fraud Alert: Transaction {transaction.id} Flagged"
        message = (
            f"A transaction has been flagged for potential fraud.\n\n"
            f"Reason: {reason}\n"
            f"Transaction Details:\n"
            f"Type: {transaction.transaction_type}\n"
            f"Amount: {transaction.amount}\n"
            f"Account: {transaction.account.account_number}\n"
            f"Date: {transaction.date}\n"
        )
        # Send email to all admins
        admin_emails = [admin.email for admin in User.objects.filter(is_staff=True)]
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, admin_emails)
        logger.info(f"Fraud alert sent for transaction {transaction.id}")
    except Exception as e:
        logger.error(f"Failed to send fraud alert for transaction {transaction.id}: {e}")


def create_notification(user, transaction):
    """
    Create a notification for the user based on the transaction type and flow.
    """
    from notifications.models import Notification  # Import here to avoid circular dependency

    try:
        if transaction.transaction_flow == "credit":
            if transaction.transaction_type == "deposit":
                message = (
                    f"A deposit of {transaction.amount} has been credited to your account. "
                    f"Your new account balance is {transaction.account.balance}."
                )
            elif transaction.transaction_type == "transfer":
                message = (
                    f"You have received a transfer of {transaction.amount} "
                    f"from {transaction.account.get_full_name()} "
                    f"on {transaction.created_at.strftime('%Y-%m-%d %H:%M:%S')}. "
                    f"Your new account balance is {transaction.account.balance}."
                )
            else:
                message = (
                    f"A credit transaction of {transaction.amount} has been processed. "
                    f"Your new account balance is {transaction.account.balance}."
                )
        elif transaction.transaction_flow == "debit":
            if transaction.transaction_type == "withdrawal":
                message = (
                    f"A withdrawal of {transaction.amount} has been processed successfully. "
                    f"Your new account balance is {transaction.account.balance}."
                )
            elif transaction.transaction_type == "transfer":
                message = (
                    f"A transfer of {transaction.amount} has been sent successfully. "
                    f"to {transaction.recipient_account.get_full_name()} "
                    f"on {transaction.created_at.strftime('%Y-%m-%d %H:%M:%S')}. "
                    f"Your new account balance is {transaction.account.balance}."
                )
            else:
                message = (
                    f"A debit transaction of {transaction.amount} has been processed. "
                    f"Your new account balance is {transaction.account.balance}."
                )
        else:
            message = (
                f"A transaction of {transaction.amount} has been processed. "
                f"Your new account balance is {transaction.account.balance}."
            )

        notification = Notification.objects.create(
            user=user,
            transaction=transaction,
            message=message,
            transaction_type=transaction.transaction_type,
            transaction_flow=transaction.transaction_flow,
        )
        logger.info(f"Notification created for {user.email}: {message}")
        return notification
    except Exception as e:
        logger.error(f"Failed to create notification for {user.email}: {str(e)}")
        return None



# def notification_request(user)