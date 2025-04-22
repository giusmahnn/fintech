from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from transactions.choices import Status
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get_unread(self, request):
        notifications = Notification.objects.filter(user=request.user, is_read=False)
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=Status.HTTP_200_OK)
    
    def get(self, request):
        user = request.user
        transaction_flow = request.query_params.get('transaction_flow')
        transaction_type = request.query_params.get('transaction_type')

        queryset = Notification.objects.filter(user=user)
        if transaction_flow:
            queryset = queryset.filter(transaction__flow=transaction_flow)
        if transaction_type:
            queryset = queryset.filter(transaction__type=transaction_type)

        queryset = queryset.order_by('-created_at')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = NotificationSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = NotificationSerializer(queryset, many=True)
        return Response(serializer.data, status=Status.HTTP_200_OK)

class NotificationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, notification_id):
        try:
            notification = Notification.objects.get(id=notification_id, user=request.user)
            if not notification.is_read:
                notification.is_read = True
                notification.save()
            serializer = NotificationSerializer(notification)
            return Response(serializer.data, status=200)
        except Notification.DoesNotExist:
            return Response({"error": "Notification not found"}, status=Status.HTTP_404_NOT_FOUND)