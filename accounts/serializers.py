import re
from rest_framework import serializers
from .utils import normalize_number, validate_password
from .models import (
    User,
    Account,
    AccountType,
    AccountLimit,
    AccountUpgradeRequest,
    Role,
)


class UserSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    password_confirmation = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'profile_picture',
            'phone_number',
            'date_of_birth',
            'email',
            'gender',
            'password',
            'password_confirmation'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
            'password_confirmation': {'write_only': True},
            'id': {'read_only': True}
        }

    def validate(self, data):
        try:
            validate_password(data["password"])
        except ValueError as e:
            raise serializers.ValidationError(str(e))
        if data["password"] != data["password_confirmation"]:
            raise serializers.ValidationError("Passwords do not match")
        # data["phone_number"] = normalize_number(data["phone_number"])
        return data
    
    def validate_phone_number(self, value):  
        """Validate the phone number and ensure it doesn't start with '0' or '+234'."""  
        if value.startswith('0'):  
            raise serializers.ValidationError("Phone number cannot start with '0'.")
        return value
    
    def create(self, validated_data):
        validated_data['phone_number'] = self.validate_phone_number(validated_data['phone_number'])  
        validated_data.pop('password_confirmation')  # Remove confirmation as it's not needed  
        user = User(**validated_data)  
        user.set_password(validated_data['password'])  # Hash the password  
        user.save()  
        return user 
    


class LoginSerializer(serializers.Serializer):
    account_number = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        account_number = data.get('account_number')
        password = data.get('password')
        try:
            account = Account.objects.get(account_number=account_number)
            user = account.user
            if user.check_password(password):
                return user
            else:
                raise serializers.ValidationError("Incorrect password")
        except Account.DoesNotExist:
            raise serializers.ValidationError("Account not found")
    