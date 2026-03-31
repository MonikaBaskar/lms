from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Course, Enrollment
from .serializers import EnrollmentSerializer, CourseSerializer

# Student enrolls in course
class EnrollStudentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Only students can enroll
        if request.user.role.name.lower() != 'student':
            return Response({"error": "Only students can enroll in courses"}, status=status.HTTP_403_FORBIDDEN)

        student = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response({"error": "course_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            print(f"Looking for course with ID: {course_id}")
            course = Course.objects.get(id=course_id)
            print(f"Course found: {course.title}")
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

        # Create enrollment if not already exists
        enrollment, created = Enrollment.objects.get_or_create(student=student, course=course)

        if not created:
            return Response({"message": "Already enrolled"}, status=status.HTTP_200_OK)

        serializer = EnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CourseEnrollmentListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=status.HTTP_404_NOT_FOUND)

        # Only teacher or admin can view enrolled students
        if request.user.role.name.lower() not in ['teacher', 'admin']:
            return Response({"error": "Only teacher or admin can view enrolled students"}, status=status.HTTP_403_FORBIDDEN)

        enrollments = Enrollment.objects.filter(course=course)
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


