from rest_framework import serializers
from .models import User, Profile, Role, Permission


class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)
    role = serializers.CharField(write_only=True) 

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def create(self, validated_data):
        role_name = validated_data.pop('role') 
        validated_data.pop('password2')

        try:
            role = Role.objects.get(name=role_name)
        except Role.DoesNotExist:
            raise serializers.ValidationError({"role": f"Role '{role_name}' does not exist."})

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

