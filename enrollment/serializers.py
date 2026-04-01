from rest_framework import serializers
from enrollment.models import Enrollment
from courses.serializers import CourseSerializer
from accounts.serializers import UserSerializer


class EnrollmentSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course',  'enrolled_at']