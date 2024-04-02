from django.urls import path
from common_components.views import (CheckProfileView,
                                     UserProfileCreateView,
                                     UserProfileView,
                                     UserProfileEditView,
                                     UserDeleteView)

urlpatterns = [
    path('check_profile/', CheckProfileView.as_view(), name='check_profile'),
    path('create_profile/', UserProfileCreateView.as_view(), name='create_profile'),
    path('view_profile/', UserProfileView.as_view(), name='view_profile'),
    path('edit_profile/', UserProfileEditView.as_view(), name='edit_profile'),
    path('delete_profile/', UserDeleteView.as_view(), name='delete_profile'),
]