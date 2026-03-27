from django.db import models
from django.contrib.auth.models import AbstractUser

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

# Custom User model
class User(AbstractUser):
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)

# Profile model
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    bio = models.TextField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    def __str__(self):
        return f"{self.first_name} {self.last_name}"