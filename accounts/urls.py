# accounts/urls.py
from django.urls import path
from .views import RegisterAPIView, LoginAPIView, LogoutAPIView
from .views import (
    ProfileView, ProfileCreateView, ProfileEditView, ProfileDeleteView,
    ProfileListStudentsView, ProfileListTeachersView, ProfileListAllView,
    CreateUserByAdmin
)

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),
    path('logout/', LogoutAPIView.as_view(), name='logout'),
    
    path('api/admin/create-user/', CreateUserByAdmin.as_view()),

    # Get own profile
    path('profile/me/', ProfileView.as_view(), name='my-profile'),

    # Get specific user (Admin only)
    path('profile/<int:user_id>/', ProfileView.as_view(), name='view-profile'),

    # List students / teachers / all (Admin only)
    path('profile/students/', ProfileListStudentsView.as_view(), name='students-list'),
    path('profile/teachers/', ProfileListTeachersView.as_view(), name='teachers-list'),
    path('profile/all/', ProfileListAllView.as_view(), name='all-users'),

    # Create profile (Admin only)
    path('profile/create/', ProfileCreateView.as_view(), name='create-profile'),

    # Edit profile (own / admin any)
    path('profile/edit/', ProfileEditView.as_view(), name='edit-profile'),
    path('profile/edit/<int:user_id>/', ProfileEditView.as_view(), name='edit-user-profile'),

    # Delete profile (own / admin any)
    path('profile/delete/me/', ProfileDeleteView.as_view(), name='delete-my-profile'),
    path('profile/delete/<int:user_id>/', ProfileDeleteView.as_view(), name='delete-user-profile'),
]


   
