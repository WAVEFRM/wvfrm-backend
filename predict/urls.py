from django.urls import path
from .views import UploadMP3File

urlpatterns = [
    path('upload_file/', UploadMP3File.as_view(), name='upload_file'),
]