from notifications.models import Notification
import logging

logger = logging.getLogger(__name__)



def create_notification(user, transaction):
    """
    Create a notification for the user based on the transaction type and flow.
    """
    message = f"Transaction {transaction.transaction_type} of {transaction.amount} has been processed."
    Notification.objects.create(
        user=user,
        transaction=transaction,
        message=message,
        transaction_type=transaction.transaction_type,
        transaction_flow=transaction.transaction_flow,
    )



def send_notification(user, message, transaction=None):
    try:
        notification = Notification.objects.create(
            user=user,
            message=message,
            transaction=transaction,
        )
        logger.info(f"Notification created for {user.email}: {message}")
        return notification
    except Exception as e:
        logger.error(f"Failed to create notification for {user.email}: {str(e)}")
        return None