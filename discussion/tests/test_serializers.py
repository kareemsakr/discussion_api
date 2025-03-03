# api/tests/test_serializers.py
from django.test import TestCase
from discussion.models import Discussion, Comment
from discussion.serializers import DiscussionSerializer, FlatCommentSerializer
from rest_framework.exceptions import ValidationError

class DiscussionSerializerTests(TestCase):
    """Unit tests for the DiscussionSerializer"""
    
    def setUp(self):
        """Create test data that will be used by test methods"""
        self.discussion_data = {
            'user': 'test_user',
            'title': 'Test Discussion',
        }
        self.discussion = Discussion.objects.create(**self.discussion_data)
        self.serializer = DiscussionSerializer(instance=self.discussion)
    
    def test_contains_expected_fields(self):
        """Test that serialized data contains the expected fields"""
        data = self.serializer.data
        self.assertCountEqual(
            data.keys(), 
            ['id', 'user', 'title', 'created_at']
        )
    
    def test_field_content(self):
        """Test that the serialized values match the model values """
        data = self.serializer.data
        self.assertEqual(data['user'], self.discussion_data['user'])
        self.assertEqual(data['title'], self.discussion_data['title'])
        self.assertIn('id', data)
        self.assertIn('created_at', data)
    
    def test_create_with_valid_data(self):
        """Test creating a new discussion with valid data"""
        serializer = DiscussionSerializer(data={
            'user': 'new_user',
            'title': 'Test discussion',
        })
        self.assertTrue(serializer.is_valid())
        discussion = serializer.save()
        self.assertEqual(discussion.user, 'new_user')
        self.assertEqual(discussion.title, 'Test discussion')
    
    def test_validation(self):
        """Test validation error for empty required fields"""
        serializer = DiscussionSerializer(data={})
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
        

class FlatCommentSerializerTests(TestCase):
    """Unit tests for the FlatCommentSerializer"""
    
    def setUp(self):
        """Create test data that will be used by test methods"""
        self.discussion = Discussion.objects.create(
            user='test_user',
            title='Test Discussion'
        )
        
        self.comment_data = {
            'discussion': self.discussion,
            'user': 'comment_user',
            'content': 'Test comment content',
            'parent': None
        }
        self.comment = Comment.objects.create(**self.comment_data)
        
        # adding data for path and level that would be added bty get_comments_flat
        self.comment_dict = {
            'id': self.comment.id,
            'discussion_id': self.discussion.id,
            'user': 'comment_user',
            'parent_id': None,
            'content': 'Test comment content',
            'created_at': self.comment.created_at,
            'level': 0,
            'path': str(self.comment.id)
        }
        
        self.serializer = FlatCommentSerializer(instance=self.comment)
    
    def test_contains_expected_fields(self):
        """Test that the serialized data contains the expected fields"""
        data = self.serializer.data
        self.assertCountEqual(
            data.keys(),
            ['id', 'discussion', 'user', 'parent', 'content', 'created_at']
        )
    
    def test_field_content(self):
        """Test that the serialized values match the model values"""
        data = self.serializer.data
        self.assertEqual(data['user'], self.comment_data['user'])
        self.assertEqual(data['content'], self.comment_data['content'])
        self.assertEqual(data['discussion'], self.discussion.id)
        self.assertIsNone(data['parent'])
        self.assertIn('id', data)
        self.assertIn('created_at', data)
    
    def test_serializes_comment_dict_with_level_and_path(self):
        """Testing serializing a dictionary representation of a comment with level and path (these fields are not a part of the comment model so testing separetely)"""
        # Create a dictionary similar to what get_comments_flat would return
        comment_dict = {
            'id': self.comment.id,
            'discussion': self.discussion,
            'user': 'comment_user',
            'parent': None,
            'content': 'Test comment content',
            'created_at': self.comment.created_at,
            'level': 0,
            'path': str(self.comment.id)
        }
        
        # use the serializer with a dictionary instead of model instance  to invlude path and level
        serializer = FlatCommentSerializer(comment_dict)
        data = serializer.data
        
        self.assertEqual(data['level'], 0)
        self.assertEqual(data['path'], str(self.comment.id))
    
    def test_create_with_valid_data(self):
        """Test creating a new comment with valid data"""
        serializer = FlatCommentSerializer(data={
            'discussion': self.discussion.id,
            'user': 'new_user',
            'content': 'new comment content',
        })
        self.assertTrue(serializer.is_valid())
        comment = serializer.save()
        self.assertEqual(comment.user, 'new_user')
        self.assertEqual(comment.content, 'new comment content')
        self.assertEqual(comment.discussion, self.discussion)
        self.assertIsNone(comment.parent)
    
    def test_create_reply_with_valid_data(self):
        """Test creating a reply to a comment"""
        serializer = FlatCommentSerializer(data={
            'discussion': self.discussion.id,
            'user': 'reply_user',
            'content': 'Reply content',
            'parent': self.comment.id
        })
        self.assertTrue(serializer.is_valid())
        reply = serializer.save()
        self.assertEqual(reply.parent, self.comment)
    
    def test_validation(self):
        """Test validation error for empty required fields"""
        serializer = FlatCommentSerializer(data={})
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)