from rest_framework import serializers
from .models import Transaction, TransactionLimitUpgradeRequest

class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for transaction details"""
    
    transaction_type = serializers.CharField(source="get_transaction_type_display", read_only=True)
    status = serializers.CharField(source="get_status_display", read_only=True)
    beneficiary_name = serializers.SerializerMethodField(source="get_beneficiary_name", read_only=True)
    recipient_account_number = serializers.CharField(source="recipient_account.account_number", read_only=True)
    narration = serializers.CharField(required=False)

    class Meta:
        model = Transaction
        fields = [
            "id",
            "transaction_type",
            "amount",
            "status",
            "recipient_account_number",
            "beneficiary_name",
            "narration",
            "date",
        ]
    def get_beneficiary_name(self, obj):
        return obj.recipient_account.user.get_fullname()


class WithdrawalSerializer(serializers.ModelSerializer):
    """Serializer for withdrawal transaction"""
    class Meta:
        model = Transaction
        fields = [
            "id",
            "amount",
            "status",
            "date",
        ]


class DepositSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            "id",
            "amount",
            "status",
            "date",
        ]


class TransactionFilterSerializer(serializers.ModelSerializer):
    """Serializer for filtering transactions by account number"""
    recipient_account = serializers.StringRelatedField()
    class Meta:
        model = Transaction
        fields = [
            "recipient_account",
            "amount",
            "status",
            "date",
            "transaction_type",
        ]



class TransactionLimitUpgradeRequestSerializer(serializers.ModelSerializer):
    """Serializer for transaction limit upgrade request"""
    class Meta:
        model = TransactionLimitUpgradeRequest
        fields = [
            'id',
            'user',
            'account',
            'status',
            'requested_daily_transfer_limit', 
            'requested_max_single_transfer_amount',
            'reason' 
        ]
        extra_kwargs = {
            'id': {'read_only': True},
            'user': {'read_only': True},
            'account': {'read_only': True},
            'status': {'read_only': True},
        }
