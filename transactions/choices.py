from django.utils.translation import gettext_lazy as _
from django.db import models



class TransactionType(models.TextChoices):
    DEPOSIT = "deposit", _("Deposit")
    WITHDRAW = "withdraw", _("Withdraw")
    TRANSFER = "transfer", _("Transfer")


class Status(models.TextChoices):
    PENDING = "pending", _("Pending")
    COMPLETED = "completed", _("Completed")
    FAILED = "failed", _("Failed")
    