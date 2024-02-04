from django.db import models
from django.contrib.auth.models import User

class SongPopResults(models.Model):
    user_profile = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    result = models.JSONField()

    def __str__(self):
        return f'SongPopResults - {self.id}'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    dob = models.DateField(null=True, blank=True)  # Date of Birth
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Creation timestamp

    def __str__(self):
        return f'{self.user.username} - Profile'
