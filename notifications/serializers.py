from rest_framework import serializers
from .models import Notification
from accounts.models import User
from django.utils import timezone
from transactions.models import Transaction



class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    transaction = serializers.StringRelatedField(read_only=True)
    message = serializers.CharField(max_length=255)
    created_at = serializers.DateTimeField(default=timezone.now)
    read_at = serializers.DateTimeField(required=False, allow_null=True)

    class Meta:
        model = Notification
        fields = ['id', 'user', 'transaction', 'message', 'created_at', 'read_at']