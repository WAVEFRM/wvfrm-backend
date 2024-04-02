from django.urls import path
from predict.views import (PopularityPredictionTaskListView, 
                           HighLevelPredictionView,
                           LowLevelPredictionView)
# , UploadMP3File

urlpatterns = [
    path('popularity_prediction_tasks/', PopularityPredictionTaskListView.as_view(), name='popularity_prediction_tasks'),
    path('high_level_prediction/', HighLevelPredictionView.as_view(), name='high_level_prediction'),
    path('low_level_prediction/', LowLevelPredictionView.as_view(), name='low_level_prediction'),

    # path('upload_file/', UploadMP3File.as_view(), name='upload_file'),
]