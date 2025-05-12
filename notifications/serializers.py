from rest_framework import serializers
from .models import Notification
from accounts.models import User
from django.utils import timezone
from transactions.models import Transaction



class NotificationSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    transaction = serializers.StringRelatedField(read_only=True)
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'user', 'transaction', 'message', 'is_read', 'created_at', 'read_at']
        read_only_fields = ['id', 'user', 'created_at', 'read_at', 'is_read']

    def get_is_read(self, obj):
        """
        Check if the notification is read or not.
        """
        return obj.read_at is not None