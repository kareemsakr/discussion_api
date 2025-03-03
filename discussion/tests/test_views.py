# api/tests/test_views.py
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from discussion.models import Discussion, Comment

# import json

class DiscussionViewSetTests(APITestCase):
    """Unittests for the DiscussionViewSet"""
    
    def setUp(self):
        """Create test data that will be used by the test methods"""
        self.discussion = Discussion.objects.create(
            user="test_user",
            title="Test Discussion"
        )
        
        # so we don't hardcodee the urls
        self.list_url = reverse('discussion-list')
        self.detail_url = reverse('discussion-detail', args=[self.discussion.id])
    
    def test_list_discussions(self):
        """Test listing all discussions"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "Test Discussion")
    
    def test_retrieve_discussion(self):
        """Test retrieving a specific discussion"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Test Discussion")
        self.assertEqual(response.data['user'], "test_user")
    
    def test_create_discussion(self):
        """Test creating a new discussion"""
        data = {
            'user': 'new user',
            'title': 'New Discussion'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Discussion.objects.count(), 2)
        self.assertEqual(response.data['title'], 'New Discussion')
        self.assertEqual(response.data['user'], 'new user')
    
    def test_create_discussion_invalid_data(self):
        """Test creating a discussion with invalid data"""
        data = {
            'user': '',  # no  username
            'title': 'New Discussion'
        }
        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('user', response.data)  # Error message for user field


class CommentViewSetTests(APITestCase):
    """Unit tests for CommentViewSet"""
    
    def setUp(self):
        """Create test data that will be used by the test methods"""
        self.discussion = Discussion.objects.create(
            user="test_user",
            title="Test Discussion"
        )
        
        self.comment = Comment.objects.create(
            discussion=self.discussion,
            user="comment user",
            content="This is a test comment"
        )
        
        self.reply = Comment.objects.create(
            discussion=self.discussion,
            user="reply user",
            content="This is a reply",
            parent=self.comment
        )
        

        self.discussion_comments_url = reverse('discussion-comments', args=[self.discussion.id])
        self.comment_replies_url = reverse('comment-replies', args=[self.discussion.id, self.comment.id])
    
    def test_list_discussion_comments(self):
        """Test listing all comments for a discussion"""
        response = self.client.get(self.discussion_comments_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # Should include both comment and reply (i.e. all levels)
        
        # Find both comment and reply in the response
        comment_data = next((c for c in response.data if c['id'] == self.comment.id), None)
        reply_data = next((c for c in response.data if c['id'] == self.reply.id), None)
        
        self.assertIsNotNone(comment_data)
        self.assertIsNotNone(reply_data)
        self.assertEqual(comment_data['content'], "This is a test comment")
        self.assertEqual(reply_data['content'], "This is a reply")
    
    def test_list_comments_with_level_filter(self):
        """Test listing comments with the level query parameter"""
        # Test level=0 (only top-level comments)
        response = self.client.get(f"{self.discussion_comments_url}?level=0")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should only include the top-level comment
        self.assertEqual(response.data[0]['id'], self.comment.id)
    
    def test_create_comment(self):
        """Test creating a new comment for a discussion"""
        data = {
            'user': 'new commenter',
            'content': 'New comment'
        }
        response = self.client.post(self.discussion_comments_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 3)  # the original + reply + new one
        self.assertEqual(response.data['user'], 'new commenter')
        self.assertEqual(response.data['content'], 'New comment')
        self.assertEqual(response.data['discussion'], self.discussion.id)
        self.assertIsNone(response.data['parent'])
    
    def test_create_reply(self):
        """Test creating a reply to an existing comment"""
        data = {
            'user': 'new replier',
            'content': 'New reply',
            'parent': self.comment.id
        }
        response = self.client.post(self.discussion_comments_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 3)  # Original + old reply + new reply
        self.assertEqual(response.data['parent'], self.comment.id)
        
        # Verify its in the database
        created_reply = Comment.objects.get(id=response.data['id'])
        self.assertEqual(created_reply.parent, self.comment)
    
    def test_create_comment_invalid_data(self):
        """Test creating a comment with invalid data"""
        data = {
            'user': '',  #no username
            'content': 'New comment'
        }
        response = self.client.post(self.discussion_comments_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('user', response.data)  # Error message for user field
    
    def test_get_comment_replies(self):
        """Test getting all replies to a specific comment"""
        response = self.client.get(self.comment_replies_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Should only include the reply
        self.assertEqual(response.data[0]['id'], self.reply.id)
        self.assertEqual(response.data[0]['content'], "This is a reply")
    
    def test_nonexistent_discussion(self):
        """Test requesting comments for a nonexistent discussion"""
        nonexistent_url = reverse('discussion-comments', args=[99999])  # This id should not exist
        response = self.client.get(nonexistent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_nonexistent_comment(self):
        """Test requesting replies for a nonexistent comment"""
        nonexistent_url = reverse('comment-replies', args=[self.discussion.id, 99999])  # This id should not exist
        response = self.client.get(nonexistent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)