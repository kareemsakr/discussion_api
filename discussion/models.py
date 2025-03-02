from django.db import models, connection

# Create your models here.
class Discussion(models.Model):
    user = models.CharField(max_length=100)
    title = models.CharField(max_length=280) # to match twitter's character count as an example
    created_at = models.DateTimeField(auto_now_add=True)

    # In case we need to add the ability to delete or close disucssions
    # STATUS_CHOICES = [
    #     ('active', 'Active'),
    #     ('deleted', 'Deleted'),
    #     ('closed', 'Closed'),
    # ]
    # status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def get_comments_flat(self):
        # Will use recursive common table expression to to get comments in a flat tree structure
        with connection.cursor() as cursor:
            cursor.execute("""
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
                SELECT * FROM comment_tree ORDER BY path;
            """, [self.id])
            
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']  # Order by newest first
        # indexes = [models.Index(fields=['user'])]  # TODO Verify if we need this


class Comment(models.Model):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, related_name='comments')
    user = models.CharField(max_length=100)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return f"Comment by {self.user} on {self.discussion.title}"
    
    class Meta:
        ordering = ['created_at']