from notifications.models import Notification

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