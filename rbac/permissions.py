from rest_framework.permissions import BasePermission

class HasPermission(BasePermission):
    """
    Custom permission class to enforce RBAC.
    """
    def has_permission(self, request, view):
        # Retrieve the required permission name from the view
        permission_name = getattr(view, "required_permission", None)
        if not permission_name:
            return True  # If no permission is required, allow access
        return request.user.is_authenticated and request.user.has_permission(permission_name)