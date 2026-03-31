from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


from .models import Course
from .serializers import CourseSerializer
from .permissions import IsAdminOrTeacher

class CreateCourseAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]

    def post(self, request):
        if request.user.role.name.lower() == "student":
            return Response({"error": "Permission denied"}, status=403)

        serializer = CourseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)  
            return Response(serializer.data)

        return Response(serializer.errors)
    
    
class CourseListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        role = user.role.name.lower() if user.role else None

        if role == "admin" or role == "student":
            courses = Course.objects.all()

        elif role == "teacher":
            courses = Course.objects.filter(created_by=user)

        else:
            return Response({"error": "Invalid role"}, status=403)

        return Response(CourseSerializer(courses, many=True).data)

class CourseUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        try:
            course = Course.objects.get(id=pk)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=404)

        user = request.user
        role = user.role.name.lower() if user.role else None

        if role == "student":
            return Response({"error": "Permission denied"}, status=403)

        if role == "teacher" and course.created_by != user:
            return Response({"error": "You can edit only your course"}, status=403)

        serializer = CourseSerializer(course, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors)

class CourseDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            course = Course.objects.get(id=pk)
        except Course.DoesNotExist:
            return Response({"error": "Course not found"}, status=404)

        user = request.user
        role = user.role.name.lower() if user.role else None

        if role != "admin":
            return Response({"error": "Permission denied"}, status=403)

        course.delete()
        return Response({"message": "Course deleted successfully"})
    
