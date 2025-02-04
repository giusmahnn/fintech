from datetime import timezone
from django.db.models.signals import post_save
from accounts.models import User, Account
from django.dispatch import receiver
from django.conf import settings
from django.urls import reverse

from .utils import send_email
from .models import Account, AccountType


@receiver(post_save, sender=User)
def create_account(sender, instance, created, **kwargs):
    """Create a default account for every new CUSTOMER"""
    if created and instance.roles == "CUSTOMER":
        default_account_type = AccountType.objects.filter(name="Savings").first()
        if not default_account_type:
            default_account_type = AccountType.objects.create(name="Savings", description="Default savings account")

        # Create a default account for the new user
        account = Account.objects.create(user=instance, account_type=default_account_type)

        if instance.email and instance.phone_number:
            send_email(
                instance.email,
                "Account Creation",
                f"Your account has been created successfully. Your account number is {instance.phone_number}"
            )
        