from django.urls import path
from .views import (
    EnrollmentListAPIView,
    EnrollmentCreateAPIView,
    EnrollmentUpdateAPIView,
    EnrollmentDeleteAPIView
)

urlpatterns = [
    path('enrollments/', EnrollmentListAPIView.as_view(), name='enrollment-list'),
    path('enrollments/create/', EnrollmentCreateAPIView.as_view(), name='enrollment-create'),
    path('enrollments/<int:enrollment_id>/update/', EnrollmentUpdateAPIView.as_view(), name='enrollment-update'),
    path('enrollments/<int:enrollment_id>/delete/', EnrollmentDeleteAPIView.as_view(), name='enrollment-delete'),
]