# accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, Role
from .serializers import RegisterSerializer
from django.contrib.auth import get_user_model
from .models import Profile
from .serializers import ProfileSerializer
# from .permissions import has_permission
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.conf import settings
import datetime

# ADMIN CREATE USER
@method_decorator(csrf_exempt, name='dispatch') 
class CreateUserByAdmin(APIView):
    authentication_classes = [JWTAuthentication]  
    permission_classes = [IsAuthenticated]

    def post(self, request):

        if not request.user.role or request.user.role.name.lower() != 'admin':
            return Response({"error": "Only admin allowed"}, status=403)

        data = request.data
        role_name = data.get('role')

        if not role_name:
            return Response({"error": "Role is required"}, status=400)

        try:
            role = Role.objects.get(name__iexact=role_name)
        except Role.DoesNotExist:
            return Response({"error": "Invalid role"}, status=400)

        serializer = RegisterSerializer(data=data)

        if serializer.is_valid():
            user = serializer.save()
            user.role = role
            user.save()

            return Response({
                "message": f"{role.name} created successfully"
            }, status=201)

        return Response(serializer.errors, status=400)
    
# register
# class RegisterAPIView(APIView):
#     authentication_classes = [] 
#     permission_classes = [AllowAny]

#     def post(self, request):
#         data = request.data
#         # role_name = 'student'

#         try:
#             role = Role.objects.get(name__iexact=data["role"].lower())
#         except Role.DoesNotExist:
#             return Response({"error": "Invalid role"}, status=400)

#         serializer = RegisterSerializer(data=data)
#         if serializer.is_valid():   
#             user = serializer.save()
#             user.role = role
#             user.save()

#             return Response({
#                 "message": f"{user.username} registered successfully",
#                 "role": user.role.name
#             }, status=201)

#         return Response(serializer.errors, status=400)
@method_decorator(csrf_exempt, name='dispatch')
class RegisterAPIView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": f"{user.username} registered successfully",
                "role": user.role.name
            }, status=201)

        return Response(serializer.errors, status=400)
    
# login
@method_decorator(csrf_exempt, name='dispatch')
class LoginAPIView(APIView):
    # authentication_classes = []  
    # permission_classes = []   

    def post(self, request):

        data = request.data
        username = data.get('username') or request.POST.get('username')
        password = data.get('password') or request.POST.get('password')

        if not username or not password:
            return Response({"error": "Username and password are required."}, status=400)

        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                "message": "Login successful",
                "role": user.role.name if user.role else None,
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }, status=200)

        return Response({"error": "Invalid credentials"}, status=401)

#logout  
# class LogoutAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         try:
#             refresh_token = request.data.get("refresh")
#             token = RefreshToken(refresh_token)
#             token.blacklist()
#             return Response({"message": "Logout successful"})
#         except Exception:
#             return Response({"error": "Invalid token"}, status=400)
@method_decorator(csrf_exempt, name='dispatch')
class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        
        if not refresh_token:
            return Response({"error": "Refresh token is required"}, status=400)
        
        try:
            # blacklist refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            # blacklist access token in redis
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                access_token_str = auth_header.split(" ")[1]
                access_token = AccessToken(access_token_str)
                jti = access_token["jti"]
                
                # store in redis until access token expires
                expiry = access_token["exp"] - int(datetime.datetime.now().timestamp())
                cache.set(f"blacklist_{jti}", "true", timeout=expiry)

            return Response({"message": "Logout successful"}, status=200)
        
        except TokenError:
            return Response({"error": "Invalid or expired refresh token"}, status=400)


User = get_user_model()

# view single profile
# class ProfileView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request, user_id=None):
#         try:
#             if user_id:
#                 profile = Profile.objects.get(user__id=user_id)
#             else:
#                 profile = Profile.objects.get(user=request.user)
#         except Profile.DoesNotExist:
#             return Response({'error': 'Profile not found'}, status=404)

#         if not has_permission(request.user, 'view_profile', target_user=profile.user):
#             return Response({'error': 'Permission denied'}, status=403)

#         serializer = ProfileSerializer(profile)
#         return Response(serializer.data, status=200)

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None):
        try:
            if user_id: 
                # only allow if own profile or admin
                if request.user.id != user_id and request.user.role.name.lower() != 'admin':
                    return Response({'error': 'Permission denied'}, status=403)
                profile = Profile.objects.get(user__id=user_id)
            else:
                profile = Profile.objects.get(user=request.user)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=404)

        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=200)
    
# List all students (Admin)
class ProfileListStudentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.role or request.user.role.name != 'admin':
            return Response({'error': 'Permission denied'}, status=403)

        students = Profile.objects.filter(user__role__name__iexact='student')
        serializer = ProfileSerializer(students, many=True)
        return Response(serializer.data, status=200)


# List all teachers (Admin)
class ProfileListTeachersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.role or request.user.role.name != 'admin':
            return Response({'error': 'Permission denied'}, status=403)

        
        teachers = Profile.objects.filter(user__role__name__iexact='teacher')
        serializer = ProfileSerializer(teachers, many=True)
        return Response(serializer.data, status=200)


# List all users (Admin)
class ProfileListAllView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.role or request.user.role.name != 'admin':
            return Response({'error': 'Permission denied'}, status=403)

        profiles = Profile.objects.exclude(user__role__name='admin')
        serializer = ProfileSerializer(profiles, many=True)
        return Response(serializer.data, status=200)


class ProfileCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        if not request.user.role or request.user.role.name.lower() != 'admin':
            return Response({"error": "Permission denied. Only admin can create profiles."}, status=403)

        data = request.data

        user_id = data.get('user_id') 
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        bio = data.get('bio')
        phone_number = data.get('phone')

        if not user_id:
            return Response({"error": "user_id is required"}, status=400)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": f"User with id {user_id} does not exist"}, status=404)

        if hasattr(user, 'profile'):
            return Response({"error": "Profile already exists for this user"}, status=400)

        profile = Profile.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            bio=bio,
            phone_number=phone_number
        )

        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=201)
    
# Edit profile
# class ProfileEditView(APIView):
#     permission_classes = [IsAuthenticated]

#     def put(self, request, user_id=None):
#         try:
#             if user_id:
#                 profile = Profile.objects.get(user__id=user_id)
#             else:
#                 profile = Profile.objects.get(user=request.user)
#         except Profile.DoesNotExist:
#             return Response({'error': 'Profile not found'}, status=404)

#         if not has_permission(request.user, 'edit_profile', target_user=profile.user):
#             return Response({'error': 'Permission denied'}, status=403)

#         serializer = ProfileSerializer(profile, data=request.data, partial=True)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=200)

#         return Response(serializer.errors, status=400)

class ProfileEditView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, user_id=None):
        
        # No user_id → just edit own profile from token
        if not user_id:
            try:
                profile = Profile.objects.get(user=request.user)
            except Profile.DoesNotExist:
                return Response({'error': 'Profile not found'}, status=404)

            serializer = ProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=200)
            return Response(serializer.errors, status=400)
        # user_id present → must be admin
        if str(request.user.role) != 'admin':
            return Response({'error': 'Permission denied. Admins only.'}, status=403)

        # Admin → check if that user_id record exists
        try:
            profile = Profile.objects.get(user__id=user_id)
        except Profile.DoesNotExist:
            return Response({'error': f'Profile with user_id {user_id} not found'}, status=404)

        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)      

# delete profile
# class ProfileDeleteView(APIView):
#     permission_classes = [IsAuthenticated]

#     def delete(self, request, user_id=None):
#         if user_id:
#             try:
#                 profile = Profile.objects.get(user__id=user_id)
#             except Profile.DoesNotExist:
#                 return Response({"error": "Profile not found"}, status=404)
#         else:
#             profile = getattr(request.user, 'profile', None)
#             if not profile:
#                 return Response({"error": "Profile not found"}, status=404)

#         if not has_permission(request.user, 'delete_profile', target_user=profile.user):
#             return Response({"error": "Permission denied"}, status=403)

#         profile.user.delete()
#         return Response({"success": f"Profile {profile.user.username} deleted"}, status=200)
    
class ProfileDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id=None):

        # No user_id → student/teacher own profile delete → NOT allowed
        if not user_id:
            if str(request.user.role) != 'admin':
                return Response({"error": "Permission denied. Only admins can delete profiles."}, status=403)

        # user_id present → must be admin
        if str(request.user.role) != 'admin':
            return Response({"error": "Permission denied. Admins only."}, status=403)

        # Admin → check if that user_id record exists
        try:
            profile = Profile.objects.get(user__id=user_id)
        except Profile.DoesNotExist:
            return Response({"error": f"Profile with user_id {user_id} not found"}, status=404)

        username = profile.user.username
        profile.user.delete()
        return Response({"success": f"Profile {username} deleted"}, status=200)

