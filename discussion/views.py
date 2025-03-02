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
        """

        # Check if discussion exists
        discussion = Discussion.objects.filter(id=discussion_id).first()
        if not discussion:
            return Response({"error": "Discussion not found"}, status=404)
            
        flat_comments = discussion.get_comments_flat()
        return Response(flat_comments)