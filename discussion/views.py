# Create your views here.
from rest_framework import viewsets, mixins
from .models import Discussion, Comment
from rest_framework.decorators import action
from rest_framework.response import Response
from .serializers import DiscussionSerializer, FlatCommentSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class DiscussionViewSet(mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    """
    API endpoints for managing discussions.

    Provides functionality to create, retrieve, and list discussions.
    """
    queryset = Discussion.objects.all()
    serializer_class = DiscussionSerializer


class CommentViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    """
    API endpoints for managing comments.
    
    Provides functionality to create comments for discussions and retrieve comment replies.
    """
    queryset = Comment.objects.all()
    serializer_class = FlatCommentSerializer

    @action(detail=True, methods=['get'])
    def replies(self, request, discussion_id=None, comment_id=None):
        """
        List all replies to a specific comment.
        
        Returns a flat list of all descendant comments (replies, replies to replies, etc.)
        with their level and path information.
        
        Parameters:
        - discussion_id: ID of the discussion the comment belongs to
        - comment_id: ID of the comment to get replies for
        
        Returns:
        - 200 OK: List of reply comments
        - 404 Commentn not found: If the comment doesn't exist or doesn't belong to the specified discussion
        """
        try:
            comment = Comment.objects.get(pk=comment_id, discussion_id=discussion_id)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=404)
            
        descendants = comment.get_replies_flat()
        return Response(descendants)

    def create(self, request, discussion_id=None, *args, **kwargs):
        """
        Create a new comment for a specific discussion or another comment (reply).
        
        The discussion ID is taken from the URL path and automatically added to the comment.
        To create a reply to another comment, include a 'parent' field with the parent comment ID.
        
        Parameters:
        - discussion_id: ID of the discussion to add the comment to
        
        Request Body:
        - user: name of the author or creator of the comment
        - content: Text content of the comment
        - parent: (Optional) ID of the parent comment if this is a reply
        
        Returns:
        - 201 Created: Successfully created comment
        - 400 Bad Request: Invalid request data
        """
        # Make a mutable copy of request.data
        data = request.data.copy()
        
        # Add the discussion_id from the URL
        data['discussion'] = discussion_id
        
        # Create a serializer with the modified data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'level', 
                openapi.IN_QUERY, 
                description="Filter comments by nesting level (0 for top-level only)", 
                type=openapi.TYPE_INTEGER,
                required=False
            )
        ]
    )
    def discussion_comments(self, request, discussion_id=None):
        """
        List all comments for a specific discussion.
        
        Returns comments in a flat tree struture with 'path' and 'level' information.
        Can be filtered by level using the 'level' query parameter.

        The 'path' variable represents the hierarchical ancestry of each comment,
        stored as a comma separated string of comment Ids (for example: '1,3,9').
        
        Parameters:
        - discussion_id: ID of the discussion to get comments for
        - level (query): Optional. If provided, only returns comments up to this nesting level.
          Level 0 returns only top-level comments, level 1 includes their direct replies, etc.
        
        Returns:
        - 200 OK: List of comments
        - 404 Discussion not Found: If the discussion doesn't exist
        """

        # Check if discussion exists
        discussion = Discussion.objects.filter(id=discussion_id).first()
        if not discussion:
            return Response({"error": "Discussion not found"}, status=404)
        
            # Check if level parameter is provided
        level_param = request.query_params.get('level', None)
        max_level = None
        
        if level_param is not None:
            try:
                max_level = int(level_param)
                if max_level < 0:
                    return Response({"error": "Level must be a non-negative integer"}, status=400)
            except ValueError:
                return Response({"error": "Level must be a valid integer"}, status=400)
            
        flat_comments = discussion.get_comments_flat(max_level=max_level)
        return Response(flat_comments)