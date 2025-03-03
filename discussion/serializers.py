from rest_framework import serializers
from .models import Discussion, Comment

class DiscussionSerializer(serializers.ModelSerializer):
    """Serializer for the Discussion model."""

    class Meta:
        model = Discussion
        fields = ['id', 'user', 'title', 'created_at'] 
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'user': {'help_text': 'Username of the discussion creator'},
            'title': {'help_text': 'Title of the discussion'},
            'created_at': {'help_text': 'Timestamp when the discussion was created'},
        }



class FlatCommentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Comment model that includes tree structure information.
    
    Provides a flat representation of comments with path and level information.
    """
    level = serializers.IntegerField(read_only=True,
                                    help_text="Nesting level of the comment (0 for top-level comments, 1 for direct replies, etc.)")
    path = serializers.CharField(read_only=True,
                                        help_text="Materialized path representing the comment's position in the tree"
)
    
    class Meta:
        model = Comment
        fields = ['id', 'discussion', 'user', 'parent', 'content', 'created_at', 'level', 'path']
        read_only_fields = ['id', 'created_at', 'level', 'path']
        extra_kwargs = {
            'discussion': {'help_text': 'ID of the discussion this comment belongs to'},
            'user': {'help_text': 'Username of the comment author'},
            'parent': {'help_text': 'Id of the parent comment if this is a reply, or null for top  level comments'},
            'content': {'help_text': 'Body of the comment'},
            'created_at': {'help_text': 'Timestamp when the comment was created'}
        }
