from django.test import TestCase  
from transactions.models import Transaction  
from accounts.models import Account, AccountType, User  
from decimal import Decimal  

class TransactionReversalTest(TestCase):  
    def setUp(self):  
        # Create a user  
        self.user = User.objects.create_user(  
            phone_number="08070426133",  
            email="test@example.com",  
            password="password123"  
        )  
        
        # Get or create an account type  
        self.account_type, _ = AccountType.objects.get_or_create(name='Savings')  
        
        # Create accounts with Decimal balances  
        self.account = Account.objects.create(  
            user=self.user,  
            balance=Decimal("1000.00"),  # Use Decimal  
            account_type=self.account_type,  
            account_number="12345678908"  # Manually set a unique account number  
        )  
        self.recipient_account = Account.objects.create(  
            user=self.user,  
            balance=Decimal("500.00"),  # Use Decimal  
            account_type=self.account_type,  
            account_number="0987654321"  # Manually set a unique account number  
        )  

    def test_reverse_withdrawal(self):
        # Simulate withdrawal effect
        self.account.balance -= Decimal("100.00")
        self.account.save()

        transaction = Transaction.objects.create(
            user=self.user,
            account=self.account,
            amount=Decimal("100.00"),
            transaction_type="withdrawal",
            status="success"
        )
        transaction.reverse_transaction()
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("1000.00"))
        self.assertEqual(transaction.status, "reversed")
  

    def test_reverse_deposit(self):
        # Simulate deposit effect
        self.account.balance += Decimal("100.00")
        self.account.save()

        transaction = Transaction.objects.create(
            user=self.user,
            account=self.account,
            amount=Decimal("100.00"),
            transaction_type="deposit",
            status="success"
        )
        transaction.reverse_transaction()
        self.account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("1000.00"))
        self.assertEqual(transaction.status, "reversed")
  

    def test_reverse_transfer(self):
        transaction = Transaction.objects.create(
            user=self.user,
            account=self.account,
            recipient_account=self.recipient_account,
            amount=Decimal("100.00"),
            transaction_type="transfer",
            status="success"
        )
        transaction.reverse_transaction()
        self.account.refresh_from_db()
        self.recipient_account.refresh_from_db()
        self.assertEqual(self.account.balance, Decimal("1000.00"))  # Sender's balance restored
        self.assertEqual(self.recipient_account.balance, Decimal("500.00"))  # Recipient's balance restored
        self.assertEqual(transaction.status, "reversed")
    
    def test_reverse_invalid_transaction(self):
        # Create a transaction that cannot be reversed
        transaction = Transaction.objects.create(
            user=self.user,
            account=self.account,
            amount=Decimal("100.00"),
            transaction_type="transfer",
            status="pending"
        )
        with self.assertRaises(ValueError):
            transaction.reverse_transaction()
    def test_reverse_nonexistent_transaction(self):
        # Attempt to reverse a nonexistent transaction
        transaction = Transaction.objects.create(
            user=self.user,
            account=self.account,
            amount=Decimal("100.00"),
            transaction_type="withdrawal",
            status="success"
        )
        transaction_id = transaction.id
        transaction.delete()
        with self.assertRaises(Transaction.DoesNotExist):
            Transaction.objects.get(id=transaction_id).reverse_transaction()


    def test_reverse_failed_transaction(self):
        # Simulate a failed transaction
        transaction = Transaction.objects.create(
            user=self.user,
            account=self.account,
            amount=Decimal("100.00"),
            transaction_type="withdrawal",
            status="failed"
        )
        with self.assertRaises(ValueError):
            transaction.reverse_transaction()

# TODO: CORRECT THE TEST CASES ON THE TRANSFER.