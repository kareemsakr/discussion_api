from rest_framework import serializers
from .models import Discussion, Comment

class DiscussionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discussion
        fields = ['id', 'user', 'title', 'created_at'] 
        read_only_fields = ['id', 'created_at']


class FlatCommentSerializer(serializers.ModelSerializer):
    level = serializers.IntegerField(read_only=True)
    path = serializers.CharField(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'discussion', 'user', 'parent', 'content', 'created_at', 'level', 'path']
        read_only_fields = ['id', 'created_at', 'level', 'path']
