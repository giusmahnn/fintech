from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from transactions.choices import Status
from transactions.pagination import CustomPagination
from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(APIView):  
    permission_classes = [IsAuthenticated] 
    throttle_classes = [UserRateThrottle]

    def get(self, request):  
        user = request.user  
        transaction_flow = request.query_params.get('transaction_flow', None)  
        transaction_type = request.query_params.get('transaction_type', None)

        queryset = Notification.objects.filter(user=user)  
  
        if transaction_flow:  
            queryset = queryset.filter(transaction__transaction_flow=transaction_flow)  
        if transaction_type:  
            queryset = queryset.filter(transaction__transaction_type=transaction_type)  
 
        queryset = queryset.order_by('-created_at')  
  
        paginator = CustomPagination()  
        page = paginator.paginate_queryset(queryset, request)  
        if page is not None:  
            serializer = NotificationSerializer(page, many=True)  
              
            return paginator.get_paginated_response(serializer.data)  
 
        serializer = NotificationSerializer(queryset, many=True)  
        return Response(serializer.data, status=Status.HTTP_200_OK)
class NotificationDetailView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]

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