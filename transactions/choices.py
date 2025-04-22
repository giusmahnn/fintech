from django.utils.translation import gettext_lazy as _
from django.db import models



class TransactionType(models.TextChoices):
    DEPOSIT = "deposit", _("Deposit")
    WITHDRAWAL = "withdrawal", _("Withdrawal")
    TRANSFER = "transfer", _("Transfer")


class Status(models.TextChoices):
    PENDING = "pending", _("Pending")
    SUCCESS = "success", _("Success")
    FAILED = "failed", _("Failed")
    REVERSED = "reversed", _("Reversed")



class TransactionFlow(models.TextChoices):
    DEBIT = "debit", _("Debit")
    CREDIT = "credit", _("Credit")