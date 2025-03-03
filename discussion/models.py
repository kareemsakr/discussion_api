from django.db import models, connection

class Discussion(models.Model):
    """
    Represents a discussion topic.
    
    A discussion can have multiple comments associated with it.
    """
    user = models.CharField(max_length=100, null=False, blank=False, help_text="Author of the discussion")
    title = models.CharField(max_length=280, null=False, blank=False, help_text="The actual discussion topic or title") # to match twitter's character count as an example
    created_at = models.DateTimeField(auto_now_add=True, help_text="Auto-generated timestamp of creation time")

    # In case we need to add the ability to delete or close disucssions
    # STATUS_CHOICES = [
    #     ('active', 'Active'),
    #     ('deleted', 'Deleted'),
    #     ('closed', 'Closed'),
    # ]
    # status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')


    def get_comments_flat(self, max_level=None):
        # Will use recursive common table expression to to get comments in a flat tree structure
        """
        Get all comments for this discussion in a flat tree structure.
        
        Args:
            max_level (int, optional): If provided, only returns comments up to this nesting level.
            None returns all levels.
        
        Returns:
            list: A list of dictionaries representing comments with level and path information.
        """
        with connection.cursor() as cursor:
            sql_query = """
                WITH RECURSIVE comment_tree AS (
                    -- Base case: Get all top-level comments for the discussion
                    SELECT 
                        c.id, 
                        c.discussion_id, 
                        c.user, 
                        c.parent_id, 
                        c.content, 
                        c.created_at, 
                        0 AS level, 
                        CAST(c.id AS VARCHAR(1000)) AS path
                    FROM discussion_comment c
                    WHERE c.discussion_id = %s AND c.parent_id IS NULL
                    
                    UNION ALL
                    
                    -- Recursive case: Get all replies to comments already in our result
                    SELECT 
                        c.id, 
                        c.discussion_id, 
                        c.user, 
                        c.parent_id, 
                        c.content, 
                        c.created_at, 
                        ct.level + 1 AS level, 
                        CONCAT(ct.path, ',', c.id) AS path
                    FROM discussion_comment c
                    JOIN comment_tree ct ON c.parent_id = ct.id
                )
                SELECT * FROM comment_tree
            """

            # Add level filter if specified
            if max_level is not None:
                sql_query += " WHERE level <= %s"
                cursor.execute(sql_query + " ORDER BY path;", [self.id, max_level])
            else:
                cursor.execute(sql_query + " ORDER BY path;", [self.id])
            
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']  # Order by newest first
        # indexes = [models.Index(fields=['user'])]  # TODO Verify if we need this


class Comment(models.Model):
    """
    Model representing a comment on a discussion.
    
    Comments can be top-level (directly on a discussion) or replies to other comments,
    forming a tree structure.
    """
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='comments', help_text="The discussion this comment belongs to")
    user = models.CharField(max_length=100, null=False, blank=False, help_text="Author of the Comment")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', help_text="Foreign key of the parent comment (if it is a reply to another comment), null if it is a top level comment")
    content = models.TextField(null=False, blank=False, help_text="Body of the comment")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Time stamp of comment creation")

    def get_replies_flat(self):
        """
        Get all replies of this comment in a flat tree structure with path and level.
        
        Returns:        
        list: A list of dictionaries representing reply comments with level and path information.
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                WITH RECURSIVE comment_tree AS (
                    -- Base case: Start with the current comment's direct replies
                    SELECT 
                        c.id, 
                        c.discussion_id, 
                        c.user, 
                        c.parent_id, 
                        c.content, 
                        c.created_at, 
                        0 AS level, 
                        CAST(c.id AS VARCHAR(1000)) AS path
                    FROM discussion_comment c
                    WHERE c.parent_id = %s
                    
                    UNION ALL
                    
                    -- Recursive case: Get replies to those replies
                    SELECT 
                        c.id, 
                        c.discussion_id, 
                        c.user, 
                        c.parent_id, 
                        c.content, 
                        c.created_at, 
                        ct.level + 1 AS level, 
                        CONCAT(ct.path, ',', c.id) AS path
                    FROM discussion_comment c
                    JOIN comment_tree ct ON c.parent_id = ct.id
                )
                SELECT * FROM comment_tree ORDER BY path;
            """, [self.id])
            
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def __str__(self):
        return f"Comment by {self.user} on {self.discussion.title}"
    
    class Meta:
        ordering = ['created_at']
