from rest_framework import serializers
from transactions.models import TransactionLimitUpgradeRequest


class TransactionLimitUpgradeRequestSerializer(serializers.ModelSerializer):
    user = serializers.EmailField(source="user.email", read_only=True)
    account_number = serializers.CharField(source="account.account_number", read_only=True)

    class Meta:
        model = TransactionLimitUpgradeRequest
        fields = [
            "id",
            "user",
            "account_number",
            "requested_daily_transfer_limit",
            "requested_max_single_transfer_amount",
            "status",
            "reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "created_at", "updated_at"]