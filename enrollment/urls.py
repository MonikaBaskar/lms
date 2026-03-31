from django.urls import path
from .views import EnrollStudentAPIView, CourseEnrollmentListAPIView

urlpatterns = [
    path('enroll/', EnrollStudentAPIView.as_view(), name='enroll-student'),
    path('course/<int:course_id>/enrollments/', CourseEnrollmentListAPIView.as_view(), name='course-enrollments'),
]