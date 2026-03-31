from rest_framework import serializers
from .models import User, Profile, Role, Permission
import re

# class RegisterSerializer(serializers.ModelSerializer):
#     password2 = serializers.CharField(write_only=True)
#     role = serializers.CharField(write_only=True) 

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password', 'password2', 'role']
#         extra_kwargs = {'password': {'write_only': True}}

#     def validate(self, attrs):
#         if attrs['password'] != attrs['password2']:
#             raise serializers.ValidationError("Passwords do not match.")
#         return attrs

#     def create(self, validated_data):
#         role_name = validated_data.pop('role') 
#         validated_data.pop('password2')

#         try:
#             role = Role.objects.get(name=role_name.lower())
#         except Role.DoesNotExist:
#             raise serializers.ValidationError({"role": f"Role '{role_name}' does not exist."})

#         user = User.objects.create_user(**validated_data)
#         user.role = role
#         user.save()
#         return user


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    role = serializers.CharField(write_only=True)
    username = serializers.CharField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def to_internal_value(self, data):
        if 'username' in data and not isinstance(data['username'], str):
            raise serializers.ValidationError({"username": "Username must be a string."})
        return super().to_internal_value(data)

    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters.")
        if len(value) > 50:
            raise serializers.ValidationError("Username must be at most 50 characters.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters.")
        if not re.search(r'[A-Z]', value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r'[!@#$%^&*(),.?\":{}|<>]', value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        return value

    def validate_role(self, value):
      if value.lower() == 'admin':
        raise serializers.ValidationError("Admin registration is not allowed.")
    
      try:
        role = Role.objects.get(name=value.lower())
      except Role.DoesNotExist:
        raise serializers.ValidationError(f"Role '{value}' does not exist.")
      return role

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        role = validated_data.pop('role')
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        user.role = role
        user.save()
        return user

class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name']

class UserSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Profile
        fields = ['id', 'user', 'first_name', 'last_name', 'bio', 'phone_number']

