from rest_framework.permissions import BasePermission

class IsAdminOrTeacher(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        role = getattr(request.user, 'role', None)
        if role is None:
            return False
        
        return role.name.lower() in ['admin', 'teacher']