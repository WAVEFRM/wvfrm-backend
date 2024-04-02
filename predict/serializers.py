from rest_framework import serializers
from predict.models import PopularityPredictionTask

class PopularityPredictionTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = PopularityPredictionTask
        fields = '__all__'