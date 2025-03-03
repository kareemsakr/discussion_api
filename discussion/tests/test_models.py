# api/tests/test_models.py
from django.test import TestCase
from django.core.exceptions import ValidationError
from discussion.models import Discussion, Comment

class DiscussionModelTests(TestCase):
    """Testing discussion model"""
    def setUp(self):
        """Create test data that will be used in our test methods"""
        self.discussion = Discussion.objects.create(
            user="testuser",
            title="Test Discussion",
        )
    
    def test_required_fields(self):
        """Test that required fields raises errors when missing"""

        # Create a discussion with empty title
        discussion = Discussion(user="testuser", title="")
        
        # This should raise a ValidationError
        with self.assertRaises(ValidationError):
            discussion.full_clean()
        
        # Create a discussion with empty user
        discussion = Discussion(user="", title="Test Title")
    
        # This should raise a ValidationError
        with self.assertRaises(ValidationError):
            discussion.full_clean()
    
    
    def test_discussion_creation(self):
        """Test that a discussion can be created with the proper field values """
        self.assertEqual(self.discussion.user, "testuser")
        self.assertEqual(self.discussion.title, "Test Discussion")
        self.assertIsNotNone(self.discussion.created_at)
    
    def test_get_comments_flat(self):
        """Test the get_comments_flat method returns correct structure"""
        # Create some comments for the discussion
        comment1 = Comment.objects.create(
            discussion=self.discussion,
            user="user1",
            content="Top level comment 1"
        )
        comment2 = Comment.objects.create(
            discussion=self.discussion,
            user="user2",
            content="Top level comment 2"
        )
        # This is a reply (parent comment not null)
        comment3 = Comment.objects.create(
            discussion=self.discussion,
            user="user3",
            content="Reply to comment 1",
            parent=comment1
        )
        
        flat_comments = self.discussion.get_comments_flat()
        
        self.assertEqual(len(flat_comments), 3)
        
        # Check if level and path are included
        for comment in flat_comments:
            self.assertIn('level', comment)
            self.assertIn('path', comment)
        
        # Check specific levels
        # Find comments by ID in results
        c1 = next((c for c in flat_comments if c['id'] == comment1.id), None)
        c3 = next((c for c in flat_comments if c['id'] == comment3.id), None)
        
        self.assertEqual(c1['level'], 0)  # Top level comment
        self.assertEqual(c3['level'], 1)  # Reply should have level 1


class CommentModelTests(TestCase):
    """Tests the Comment model"""
    
    def setUp(self):
        """Create test data that will be used by in the test methods"""
        self.discussion = Discussion.objects.create(
            user="testuser",
            title="Test Discussion"
        )
        self.comment = Comment.objects.create(
            discussion=self.discussion,
            user="commenter_name",
            content="This is a test comment"
        )
        
    def test_required_fields(self):
        """test that required fields raise appropriate errors when missing"""
        
        # Test missing discussion (FK)
        comment = Comment(user="testuser", content="Comment without discussion")
        with self.assertRaises(ValidationError):
            comment.full_clean()
        
        # Test no user provided
        comment = Comment(discussion=self.discussion, user="", content="Comment with empty user")
        with self.assertRaises(ValidationError):
            comment.full_clean()
        
        # Test empty content
        comment = Comment(discussion=self.discussion, user="testuser", content="")
        with self.assertRaises(ValidationError):
            comment.full_clean()
        
        # Test multiple empty fields
        comment = Comment(discussion=self.discussion, user="", content="")
        with self.assertRaises(ValidationError):
            comment.full_clean()
    
    
    def test_comment_creation(self):
        """Test that a comment can be created with the correct field values"""
        self.assertEqual(self.comment.user, "commenter_name")
        self.assertEqual(self.comment.content, "This is a test comment")
        self.assertIsNone(self.comment.parent)
        self.assertIsNotNone(self.comment.created_at)
    
    
    def test_discussion_relationship(self):
        """Test the 2 way relationship between comment and discussion"""
        self.assertEqual(self.comment.discussion, self.discussion)
        # Check reverse relationship
        self.assertEqual(self.discussion.comments.first(), self.comment)
    
    def test_parent_child_relationship(self):
        """Test the parent child relationship between comments"""
        # Create a reply to our comment
        reply = Comment.objects.create(
            discussion=self.discussion,
            user="reply_user",
            content="This is a reply to a comment",
            parent=self.comment
        )
        
        # Check the relationship
        self.assertEqual(reply.parent, self.comment)
        # Check reverse relationship
        self.assertEqual(self.comment.replies.first(), reply)
    
    def test_get_replies_flat(self):
        """Test the get_replies_flat method returns correct srtucture"""
        # creating nested replies
        reply1 = Comment.objects.create(
            discussion=self.discussion,
            user="user1",
            content="First reply",
            parent=self.comment
        )
        reply2 = Comment.objects.create(
            discussion=self.discussion,
            user="user2",
            content="Second reply",
            parent=self.comment
        )
        reply_to_reply = Comment.objects.create(
            discussion=self.discussion,
            user="user3",
            content="Reply to first reply",
            parent=reply1
        )
        
        # Get replies
        replies = self.comment.get_replies_flat()
        
        # assert basic structure
        self.assertEqual(len(replies), 3)
        
        # Check that level/path are included
        for desc in replies:
            self.assertIn('level', desc)
            self.assertIn('path', desc)
        
        # Find specific replies
        r1 = next((r for r in replies if r['id'] == reply1.id), None)
        rr = next((r for r in replies if r['id'] == reply_to_reply.id), None)
        print('r1', r1)
        print('rr', rr)
        # Check levels
        self.assertEqual(r1['level'], 0)  # Direct reply
        self.assertEqual(rr['level'], 1)  # Reply to a  reply