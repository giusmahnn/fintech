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
        return data
    
    def validate_phone_number(self, value):
        if not re.match(r"^\+234\d{10}$|^0\d{10}$", value):
            raise serializers.ValidationError("Invalid phone number")
        try:
            return normalize_number(value)
        except ValueError as e:
            raise serializers.ValidationError(str(e))
    
    def create(self, validated_data): 
        validated_data.pop('password_confirmation')  # Remove password confirmation from validated data as it is not needed for user creation  
        # Ensure the password is hashed before saving the user
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


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username")
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    phone_number = serializers.CharField(source="user.phone_number", read_only=True)
    profile_picture = serializers.ImageField(source="user.profile_picture")

    class Meta:
        model = Account
        fields = [
            "account_number",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "profile_picture",
        ]
        extra_kwargs = {
            "account_number": {"read_only": True},
        }

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        user = instance.user
        user.username = user_data.get("username", user.username)
        user.profile_picture = user_data.get("profile_picture", user.profile_picture)
        user.save()
        return super().update(instance, validated_data)
    
    
class ResetPasswordSerializer(serializers.Serializer):
    otp = serializers.CharField(required=True,write_only=True)
    password = serializers.CharField(write_only=True)
    password_confirmation = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            validate_password(data["password"])
        except ValueError as e:
            raise serializers.ValidationError(str(e))
        if data["password"] != data["password_confirmation"]:
            raise serializers.ValidationError("Passwords do not match")
        return data
    