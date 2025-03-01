from django.db import models

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
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-created_at']  # Order by newest first

