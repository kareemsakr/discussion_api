# Create your views here.
from rest_framework import viewsets, mixins
from .models import Discussion
from .serializers import DiscussionSerializer

class DiscussionViewSet(mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    """
    API endpoint that allows retrieve, list and create discussions.
    """
    queryset = Discussion.objects.all()
    serializer_class = DiscussionSerializer