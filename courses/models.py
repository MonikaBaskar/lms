# courses/models.py

from django.db import models
from accounts.models import User

class Course(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE,  related_name='courses_created')
    duration = models.IntegerField()
    is_published = models.BooleanField(default=False)
    teacher = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='courses'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

