from django.urls import path
from .views import (
    NotificationListView,
    # NotificationDetailView,
    MarkNotificationAsReadView,
    MarkNotificationAsUnreadView,
    DeleteNotificationView,
)


urlpatterns = [
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    # path('notifications/<int:notification_id>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('notifications/<int:notification_id>/mark-as-read/', MarkNotificationAsReadView.as_view(), name='mark-as-read'),
    path('notifications/<int:notification_id>/mark-as-unread/', MarkNotificationAsUnreadView.as_view(), name='mark-as-unread'),
    path('notifications/<int:notification_id>/delete/', DeleteNotificationView.as_view(), name='delete-notification'),
]