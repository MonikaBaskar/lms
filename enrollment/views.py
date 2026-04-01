from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Course, Enrollment, User
from .serializers import EnrollmentSerializer

#get
class EnrollmentListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = request.user.role.name.lower()

        try:
            if role == 'student':
                enrollments = Enrollment.objects.filter(
                    student=request.user
                ).select_related('student', 'course')

            elif role == 'teacher':
                enrollments = Enrollment.objects.filter(
                    course__teacher=request.user
                ).select_related('student', 'course')

            elif role == 'admin':
                enrollments = Enrollment.objects.all().select_related('student', 'course')

            else:
                return Response(
                    {"error": "Unauthorized role"},
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = EnrollmentSerializer(enrollments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


#post

class EnrollmentCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        role = request.user.role.name.lower()

        try:
            course_id = request.data.get('course_id')
            if not course_id:
                return Response(
                    {"error": "course_id is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                course = Course.objects.get(id=course_id)
            except Course.DoesNotExist:
                return Response(
                    {"error": "Course not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Student
            if role == 'student':
                enrollment, created = Enrollment.objects.get_or_create(
                    student=request.user,
                    course=course
                )
                if not created:
                    return Response(
                        {"message": "Already enrolled"},
                        status=status.HTTP_200_OK
                    )
                serializer = EnrollmentSerializer(enrollment)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            # Teacher
            elif role == 'teacher':
                if course.teacher != request.user:
                    return Response(
                        {"error": "You can only enroll students in your own course"},
                        status=status.HTTP_403_FORBIDDEN
                    )
                student_id = request.data.get('student_id')
                if not student_id:
                    return Response(
                        {"error": "student_id is required"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                try:
                    student = User.objects.get(id=student_id, role__name__iexact='student')
                except User.DoesNotExist:
                    return Response(
                        {"error": "Student not found"},
                        status=status.HTTP_404_NOT_FOUND
                    )
                enrollment, created = Enrollment.objects.get_or_create(
                    student=student,
                    course=course
                )
                if not created:
                    return Response(
                        {"message": "Student already enrolled"},
                        status=status.HTTP_200_OK
                    )
                serializer = EnrollmentSerializer(enrollment)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            #  Admin
            elif role == 'admin':
                student_ids = request.data.get('student_ids')

                # Bulk
                if student_ids:
                    enrolled = []
                    already_enrolled = []
                    failed = []

                    for sid in student_ids:
                        try:
                            student = User.objects.get(id=sid, role__name__iexact='student')
                            enrollment, created = Enrollment.objects.get_or_create(
                                student=student,
                                course=course
                            )
                            if created:
                                enrolled.append(sid)
                            else:
                                already_enrolled.append(sid)
                        except User.DoesNotExist:
                            failed.append(sid)

                    return Response({
                        "message": "Bulk enrollment processed",
                        "enrolled": enrolled,
                        "already_enrolled": already_enrolled,
                        "failed": failed
                    }, status=status.HTTP_201_CREATED)

                # Single
                else:
                    student_id = request.data.get('student_id')
                    if not student_id:
                        return Response(
                            {"error": "student_id or student_ids is required"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    try:
                        student = User.objects.get(id=student_id)
                    except User.DoesNotExist:
                        return Response(
                            {"error": "Student not found"},
                            status=status.HTTP_404_NOT_FOUND
                        )
                    enrollment, created = Enrollment.objects.get_or_create(
                        student=student,
                        course=course
                    )
                    if not created:
                        return Response(
                            {"message": "Already enrolled"},
                            status=status.HTTP_200_OK
                        )
                    serializer = EnrollmentSerializer(enrollment)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)

            else:
                return Response(
                    {"error": "Unauthorized role"},
                    status=status.HTTP_403_FORBIDDEN
                )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



# put
class EnrollmentUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, enrollment_id):
        role = request.user.role.name.lower()

        try:
            enrollment = Enrollment.objects.select_related(
                'student', 'course', 'course__teacher'
            ).get(id=enrollment_id)
        except Enrollment.DoesNotExist:
            return Response(
                {"error": "Enrollment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            # Student
            if role == 'student':
                if enrollment.student != request.user:
                    return Response(
                        {"error": "You can only update your own enrollment"},
                        status=status.HTTP_403_FORBIDDEN
                    )

            # Teacher
            elif role == 'teacher':
                if enrollment.course.teacher != request.user:
                    return Response(
                        {"error": "You can only update enrollments in your own course"},
                        status=status.HTTP_403_FORBIDDEN
                    )

            # Admin
            elif role == 'admin':
                pass

            else:
                return Response(
                    {"error": "Unauthorized role"},
                    status=status.HTTP_403_FORBIDDEN
                )

            is_active = request.data.get('is_active')
            if is_active is None:
                return Response(
                    {"error": "is_active field is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            enrollment.is_active = is_active
            enrollment.save()

            serializer = EnrollmentSerializer(enrollment)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


# delete
class EnrollmentDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, enrollment_id):
        role = request.user.role.name.lower()

        try:
            enrollment = Enrollment.objects.select_related(
                'student', 'course', 'course__teacher'
            ).get(id=enrollment_id)
        except Enrollment.DoesNotExist:
            return Response(
                {"error": "Enrollment not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            # Student
            if role == 'student':
                if enrollment.student != request.user:
                    return Response(
                        {"error": "You can only delete your own enrollment"},
                        status=status.HTTP_403_FORBIDDEN
                    )
                enrollment.delete()
                return Response(
                    {"message": "Enrollment dropped successfully"},
                    status=status.HTTP_200_OK
                )

            # Teacher
            elif role == 'teacher':
                if enrollment.course.teacher != request.user:
                    return Response(
                        {"error": "You can only remove students from your own course"},
                        status=status.HTTP_403_FORBIDDEN
                    )
                enrollment.delete()
                return Response(
                    {"message": "Student removed from course successfully"},
                    status=status.HTTP_200_OK
                )

            # Admin
            elif role == 'admin':
                enrollment.delete()
                return Response(
                    {"message": "Enrollment deleted successfully"},
                    status=status.HTTP_200_OK
                )

            else:
                return Response(
                    {"error": "Unauthorized role"},
                    status=status.HTTP_403_FORBIDDEN
                )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )