from django.urls import path
from .views import UserProfileCreateView,UserProfileView,SongView
urlpatterns = [
    path('create_profile/', UserProfileCreateView.as_view(), name='create_profile'),
    path('view_profile/', UserProfileView.as_view(), name='view_profile'),
    path('view_songs/', SongView.as_view(), name='view_songs'),
    
]