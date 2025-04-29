from django.db import models

# Create your models here.
class Permission(models.Model):
    """Defines specific permissions for actions."""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Role(models.Model):
    """Defines roles and their associated permissions."""
    name = models.CharField(max_length=50, unique=True)
    permissions = models.ManyToManyField(Permission, related_name="roles")
    parent_role = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="child_roles"
    )

    def get_all_permissions(self):
        """Recursively fetch all permissions, including inherited ones."""
        permissions = set(self.permissions.all())
        if self.parent_role:
            permissions.update(self.parent_role.get_all_permissions())
        return permissions

    def __str__(self):
        return self.name