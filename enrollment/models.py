from django.db import models
from django.conf import settings
from courses.models import Course
from django.contrib.auth import get_user_model  # ✅ இப்படி import பண்ணு

User = get_user_model() 


class Enrollment(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role__name': 'student'})
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        unique_together = ('student', 'course')  # prevent duplicate enrollment

    def __str__(self):
        return f"{self.student.username} → {self.course.title}"