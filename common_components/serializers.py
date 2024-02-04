# serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile,SongPopResults

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):


    class Meta:
        model = UserProfile
        fields = '__all__'
        
        
class SongPopResultsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SongPopResults
        fields = '__all__'