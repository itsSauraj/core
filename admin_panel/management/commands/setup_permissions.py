from django.core.management.base import BaseCommand
from admin_panel.roles_and_permissions.permissions import permission_manager

class Command(BaseCommand):
    help = 'Set up roles and permissions for the application'

    def handle(self, *args, **kwargs):
        permission_manager.refresh_permissions_in_store()
        self.stdout.write(self.style.SUCCESS("Roles and permissions setup complete."))

