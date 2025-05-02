from rest_framework import serializers
from accounts.models import AccountUpgradeRequest, User
from accounts.utils import validate_password
from transactions.models import TransactionLimitUpgradeRequest



class CreateAdminSerializer(serializers.ModelSerializer):
    """
    Serializer for creating an admin user.
    """
    password_confirmation = serializers.CharField(write_only=True) 
    class Meta:
        model = User
        fields = [
            'id', 
            'first_name', 
            'last_name', 
            'email', ''
            'phone_number', 
            'password',
            'password_confirmation'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'password_confirmation': {'write_only': True},
            'id': {'read_only': True}
        }


    def validate(self, data):
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email already exists")
        try:
            validate_password(data['password'])
        except serializers.ValidationError as e:
            raise serializers.ValidationError(str(e))
        if data["password"] != data.get("password_confirmation"):
            raise serializers.ValidationError("Passwords do not match")
        return data


    def create(self, validated_data):
        """
        Create a new admin user and hash the password.
        """
        validated_data.pop('password_confirmation')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data, password=password)
        return user
    



class AdminLoginSerializer(serializers.Serializer):
    """
    Serializer for admin user login.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)


    def validate(self, data):  
        email = data.get('email')  
        password = data.get('password')  
        print("email:", email)
        print("password:", password)

        if not email or not password:  
            raise serializers.ValidationError("Email and password are required.")  

        try:  
            user = User.objects.get(email=email)  
        except User.DoesNotExist:  
            raise serializers.ValidationError("Account not found.")  
        print("pass", user.check_password(password))
        if not user.check_password(password):  
            raise serializers.ValidationError("Incorrect password.")  

        # Attach user object for use after validation  
        data['user'] = user  
        return data  




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