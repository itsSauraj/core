from django.core.management.base import BaseCommand
from admin_panel.roles_and_permissions.roles import roles_manager


class Command(BaseCommand):
    help = 'Set up roles and permissions for the application'

    def handle(self, *args, **kwargs):
        roles_manager.generate_default_groups()
        self.stdout.write(self.style.SUCCESS("Roles and permissions setup complete."))