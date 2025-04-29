from django.utils.translation import gettext_lazy as _
from django.db import models


class Gender(models.TextChoices):
    MALE = 'M', _('Male')
    FEMALE = 'F', _('Female')



class AccountType(models.TextChoices):
    SAVINGS = 'SAVINGS', _('Savings')
    CHECKING = 'CHECKING', _('Checking')
    CREDIT = 'CREDIT', _('Credit')


class UpgradeRequest(models.TextChoices):
    PENDING = 'PENDING', _('Pending')
    APPROVED = 'APPROVED', _('Approved')
    REJECTED = 'REJECTED', _('Rejected')

# class Role(models.TextChoices):
#     ADMIN = 'ADMIN', _('Admin')
#     CUSTOMER = 'CUSTOMER', _('Customer')
#     SUPPORT = 'SUPPOT', _('Support')