from django.core.management.base import BaseCommand
from rbac.models import Role, Permission

class Command(BaseCommand):
    help = "Seed initial roles and permissions"

    def handle(self, *args, **kwargs):
        # Define permissions
        permissions = [
            {"name": "can_reverse_transaction", "description": "Can reverse transactions"},
            {"name": "can_approve_limit_upgrade", "description": "Can approve transaction limit upgrades"},
            {"name": "can_view_transaction_history", "description": "Can view transaction history"},
            {"name": "can_view_upgrade_requests", "description": "Can view transaction limit upgrade requests"},
            {"name": "can_manage_upgrade_requests", "description": "Can approve or reject transaction limit upgrade requests"},
    
        ]

        # Create permissions
        for perm_data in permissions:
            Permission.objects.get_or_create(name=perm_data["name"], defaults={"description": perm_data["description"]})

        # Define roles
        roles = [
            {"name": "Admin", "permissions": ["can_reverse_transaction", "can_approve_limit_upgrade", "can_view_transaction_history"]},
            {"name": "Support", "permissions": ["can_approve_limit_upgrade", "can_view_transaction_history"]},
            {"name": "Customer", "permissions": ["can_view_transaction_history"]},
        ]

        # Create roles and assign permissions
        for role_data in roles:
            role, created = Role.objects.get_or_create(name=role_data["name"])
            for perm_name in role_data["permissions"]:
                permission = Permission.objects.get(name=perm_name)
                role.permissions.add(permission)

        self.stdout.write(self.style.SUCCESS("Roles and permissions seeded successfully."))