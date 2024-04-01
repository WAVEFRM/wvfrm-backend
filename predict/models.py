from django.db import models
try:
    from django.db.models import JSONField
except ImportError:
    from django.contrib.postgres.fields import JSONField
from django.utils import timezone
from common_components.models import UserProfile

class PopularityPredictionTask(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    song_file_url = models.CharField(max_length=255, null=True, blank=True)
    result = JSONField(default=dict)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
