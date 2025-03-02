# Create your views here.
from rest_framework import viewsets, mixins
from .models import Discussion, Comment
from rest_framework.response import Response
from .serializers import DiscussionSerializer, FlatCommentSerializer

class DiscussionViewSet(mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    """
    API endpoint that allows retrieve, list and create discussions.
    """
    queryset = Discussion.objects.all()
    serializer_class = DiscussionSerializer


class CommentViewSet(mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    """
    API endpoint that allows retrieve all comments for a discussion and add comments to discussions or other comments.
    Query parameters:
    """
    queryset = Comment.objects.all()
    serializer_class = FlatCommentSerializer

    def create(self, request, discussion_id=None, *args, **kwargs):
        """
        Create a comment for the specified discussion.
        The discussion_id is taken from the URL path rather than requiring it in the request body.
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

    def discussion_comments(self, request, discussion_id=None):
        """
        Get all comments for a discussion in a flat tree structure.

        - level: Integer. If specified, returns comments up to this level.
             Level 0 returns only top-level comments.
             Level 1 returns top-level comments and direct replies.
             If not specified, returns all comments for the  given discussion id.
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