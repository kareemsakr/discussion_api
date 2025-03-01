from rest_framework import serializers
from .models import Discussion

class DiscussionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discussion
        fields = ['id', 'user', 'title', 'created_at'] # , 'status'
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {'user': {'required': True}}  # Extra validation
