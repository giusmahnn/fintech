import datetime
import re
from django.db import models
from django.db import transaction
import logging
from django.contrib.auth.models import AbstractUser, BaseUserManager
from rbac.models import Role
from django.utils.timezone import now
from .choices import (
    Gender,
    AccountType,
    UpgradeRequest
)
# Create your models here.

logger = logging.getLogger(__name__)

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email is required")
        email=self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The email is required")
        user = self.create_user(email=email, password=password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        admin_role = Role.objects.get(name="Admin")
        user.roles.set([admin_role])
        user.save()
        return user



class User(AbstractUser):
    username = models.CharField(max_length=150, blank=True, null=True, unique=True)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default="profile_images/default-profile-image.png", 
                                        blank=True, null=True)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)  # "YYYY-MM-DD"
    email = models.EmailField(max_length=255, unique=True)
    gender = models.CharField(max_length=10, choices=Gender.choices, blank=True, null=True)
    date_joined = models.DateTimeField(default=now)
    roles = models.ManyToManyField(Role, related_name="users")
    last_login = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    otp = models.IntegerField(blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    objects = UserManager()
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
    def get_fullname(self):
        return f"{self.first_name} {self.last_name}"
    
    def verify_otp(self, otp):
        if self.otp == otp:
            self.is_verified = True
            self.otp = None
            self.otp_created_at = None
            self.save()
            return True
        return False
    
    def otp_created(self):
        if self.otp:
            self.otp_created_at = datetime.datetime.now(datetime.timezone.utc)
            return True

    
    def reset_otp(self):
        self.otp = None
        self.otp_created_at = None
        self.save()

    def has_permission(self, permission_name):
        """Check if the user has a specific permission."""
        for role in self.roles.all():
            if permission_name in [perm.name for perm in role.get_all_permissions()]:
                return True
        return False

    def has_role(self, role_name):
        return self.roles.filter(name=role_name).exists()
    def is_admin(self):
        return self.has_role('Admin')
    def is_customer(self):
        return self.has_role('Customer')
    def is_support(self):
        return self.has_role('Support')
    

class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="accounts")
    account_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    account_type = models.ForeignKey('AccountType', on_delete=models.PROTECT, related_name='accounts')
    daily_transfer_limit = models.DecimalField(max_digits=15, decimal_places=2, default=5000.00)
    max_single_transfer_amount = models.DecimalField(max_digits=15, decimal_places=2, default=1000.00)
    flagged = models.BooleanField(default=False)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default='NGR') 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return f"{self.account_number} ({self.user.get_fullname()})"
    
    def normalize_phone(self):
        """Convert phone number to a standard 10-digit format."""
        if not self.user.phone_number:
            raise ValueError("Phone number is required to generate account number.")
        phone = re.sub(r'\D', '', self.user.phone_number)  # Remove non-numeric characters

        if phone.startswith("234"):  # Handle +234 or 234 cases
            return '0' + phone[3:]  # Convert '2348123456789' → '08123456789'
        elif phone.startswith("0") and len(phone) == 11:  # Already valid
            return phone
        else:
            raise ValueError("Invalid Nigerian phone number format")

    def save(self, *args, **kwargs):
        if not self.account_number:
            self.account_number = self.normalize_phone()[1:]  # Remove first digit → Get 10-digit number
        super().save(*args, **kwargs)

    def is_mini_balance_violated(self):
        return self.balance < self.account_type.min_balance
    
    def can_withdraw(self, amount):
        return self.balance >= amount and not self.is_mini_balance_violated()
    
    def is_max_balance_violated(self):
        if self.account_type.max_balance:
            return self.balance > self.account_type.max_balance
        return False
    
    def get_daily_transfer_limit(self):
        return self.account_type.limits.daily_transfer_limit
    
    @classmethod
    def create_account(cls, user, account_type, initial_balance=0.00):
        if initial_balance < account_type.min_balance:
            raise ValueError("Initial balance is less than the minimum balance required")
        if account_type.max_balance and initial_balance > account_type.max_balance:
            raise ValueError("Initial balance exceeds the maximum balance allowed")
        account = cls(user=user, 
                    account_type=account_type, 
                    balance=initial_balance
                    )
        return account

class AccountType(models.Model):
    name = models.CharField(max_length=50, choices=AccountType.choices, unique=True, default="Savings")  # e.g., Savings, Checking, Credit
    description = models.TextField(blank=True, null=True)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # Annual interest rate
    min_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)  # Minimum balance required
    max_balance = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)  # Maximum balance allowed
    daily_transfer_limit = models.DecimalField(max_digits=15, decimal_places=2, default=5000.00)  # Default daily transfer limit
    max_single_transfer_amount = models.DecimalField(max_digits=15, decimal_places=2, default=1000.00)  # Default Max amount per transaction
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.description or 'No description'}"
    
    

class AccountUpgradeRequest(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='upgrade_requests')
    requested_account_type = models.ForeignKey(AccountType, on_delete=models.CASCADE, related_name='upgrade_requests')
    status = models.CharField(max_length=10, choices=UpgradeRequest.choices, default=UpgradeRequest.PENDING)  # pending, approved, rejected
    reason = models.TextField(blank=True, null=True)
    action_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="action_request", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Upgrade request for {self.account.user.phone_number} to {self.requested_account_type.name}"

    def approve(self, admin_user):  
        if self.status != UpgradeRequest.PENDING:
            raise ValueError("Only pending requests can be approved")
        if self.status == UpgradeRequest.REJECTED:
            raise ValueError("Rejected requests cannot be approved")
        if self.account.account_type == self.requested_account_type:  
            raise ValueError("Account is already of the requested type")  
        try:
            with transaction.atomic():  
                self.account.account_type = self.requested_account_type  
                self.action_by = admin_user
                self.status = UpgradeRequest.APPROVED    
                self.account.save()  
                self.save()
        except Exception as e:
            logger.error(f"Error approving upgrade request {self.account}: {e}")
            raise ValueError(f"Upgrade request approval failed: {str(e)}")


    def reject(self, admin_user):
        if self.status != UpgradeRequest.PENDING:
            raise ValueError("Only pending requests can be rejected.")
        try:
            with transaction.atomic():
                self.status = UpgradeRequest.REJECTED
                self.action_by = admin_user  # Assign the admin user
                self.save()
        except Exception as e:
            logger.error(f"Error rejecting upgrade request {self.account}: {e}")
            raise ValueError(f"Upgrade request rejection failed: {str(e)}")

        
        

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(default=now)
    metadata = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.user} - {self.action} at {self.timestamp}"