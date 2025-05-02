from rest_framework.permissions import BasePermission

def has_permission(user, permission_name):
    """
    Check if the user has the specified permission.
    """
    # Check if the user has the permission through their roles
    for role in user.roles.all():
        if role.permissions.filter(name=permission_name).exists():
            return True

    return False






class HasPermission(BasePermission):
    """
    Custom permission class to enforce RBAC.
    """
    def has_permission(self, request, view):
        # Retrieve the required permission name from the view
        permission_name = getattr(view, "required_permission", None)
        if not permission_name:
            return True  # If no permission is required, allow access

        # Check if the user is authenticated and has the required permission
        if request.user.is_authenticated and has_permission(request.user, permission_name):
            return True

        return False