from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DiscussionViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'discussions', DiscussionViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('discussions/<int:discussion_id>/comments/', 
     CommentViewSet.as_view({'get': 'discussion_comments', 'post': 'create'}), 
     name='discussion-comments'),
    path('discussions/<int:discussion_id>/comments/<int:comment_id>/replies/', 
     CommentViewSet.as_view(({'get': 'replies'})), 
     name='comment-comments')
]