from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
# Role table
class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

# Permission table
class Permission(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name

# Role-Permission mapping
class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    class Meta:
        unique_together = ('role', 'permission')

from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):

    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        user = self.create_user(email, username, password, **extra_fields)

        # 🔥 AUTO ASSIGN ADMIN ROLE
        from accounts.models import Role
        admin_role, _ = Role.objects.get_or_create(name="admin")
        user.role = admin_role
        user.save()

        return user
    
# Custom User model
class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50)  # no longer the USERNAME_FIELD
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

    USERNAME_FIELD = 'email'           # email is used for login/auth
    REQUIRED_FIELDS = ['username']     # required when creating superuser

    objects = CustomUserManager()
# Profile model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    bio = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    def __str__(self):
        return f"{self.first_name} {self.last_name}"