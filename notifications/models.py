from django.db import models
from django.utils.timezone import now






class Notification(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    transaction = models.ForeignKey("transactions.Transaction", on_delete=models.CASCADE, null=True, blank=True)
    message = models.TextField()
    transaction_type = models.CharField(max_length=10, null=True, blank=True)
    transaction_flow = models.CharField(max_length=10, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"Notification for {self.user.email} - {self.message} - {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


    def is_read(self):
        return self.read_at is not None

    def mark_as_read(self):
        self.read_at = now()
        self.save()

    def mark_as_unread(self):
        self.read_at = None
        self.save()

    def get_notification_summary(self):
        return f"{self.message[:50]}..." if len(self.message) > 50 else self.message