# courses/urls.py

from django.urls import path
from .views import CreateCourseAPIView, CourseListAPIView, CourseUpdateAPIView, CourseDeleteAPIView

urlpatterns = [
     path('create/', CreateCourseAPIView.as_view()),
     path('viewCourses/', CourseListAPIView.as_view(), name='course-list'),
     path('<int:pk>/', CourseUpdateAPIView.as_view(), name='course-update'),
     path('<int:pk>/delete/', CourseDeleteAPIView.as_view(), name='course-delete'),
    
]