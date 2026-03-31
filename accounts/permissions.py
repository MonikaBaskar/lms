# from .models import RolePermission

# def has_permission(user, perm_name, target_user=None):
#     if not user.role:
#         return False

#     # Admin can do everything
#     if user.role.name.lower() == 'admin':
#         return True

#     # Teachers/Students cannot delete anyone
#     if perm_name == 'delete_profile':
#         return False

#     # Teacher/Student: access only own profile for other actions
#     if target_user and user.id != target_user.id:
#         return False

#     # Check role-permission mapping
#     return RolePermission.objects.filter(
#         role=user.role,
#         permission__name=perm_name
#     ).exists()

