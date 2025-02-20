from rest_framework import serializers
from .models import Transaction

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