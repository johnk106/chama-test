from django.contrib.auth.models import User
from django.db import models


class UserFcmTokens(models.Model):
    token = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)



class UserNotificationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_title = models.TextField()
    notification_body = models.TextField()
    purpose = models.CharField(max_length=250,null=True)
    created_at = models.DateTimeField(auto_now_add=True, editable=True)
    updated_at = models.DateTimeField(auto_now=True, editable=True)
