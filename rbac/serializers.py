from rest_framework import serializers
from transactions.models import TransactionLimitUpgradeRequest
from accounts.models import AccountUpgradeRequest


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




class AccountUpgradeRequestSerializer(serializers.ModelSerializer):
    user = serializers.EmailField(source="user.email", read_only=True)
    account_number = serializers.CharField(source="account.account_number", read_only=True)

    class Meta:
        model = AccountUpgradeRequest
        fields = [
            "id",
            "user",
            "account_number",
            "requested_account_type",
            "status",
            "reason",
            "approved_by",
            "rejected_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["status", "created_at", "updated_at"]
        extra_kwargs = {
            "requested_account_type": {
                "required": True,
                "allow_null": False,
            },
            "reason": {
                "required": True,
                "allow_null": False,
            },
        }
        def validate_requested_account_type(self, value):
            if not value:
                raise serializers.ValidationError("Requested account type is required.")
            return value
        def validate_reason(self, value):
            if not value:
                raise serializers.ValidationError("Reason is required.")
            return value