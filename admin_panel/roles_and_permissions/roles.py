from admin_panel.roles_and_permissions.permissions import permission_manager
from django.contrib.auth.models import Group

from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

class RolesManager:
    @staticmethod
    def delete(group_id):
        Group.objects.filter(id=group_id).delete()

    @staticmethod
    def create(name, permissions=None):
        group, created = Group.objects.get_or_create(name=name)
        group.permissions.set(permissions)
        group.save()
        return group

    @staticmethod
    def get(group_id):
        return Group.objects.get(id=group_id)

    @staticmethod
    def get_name_by_ids(group_ids):
        return [resp['name'] for resp in Group.objects.filter(id__in=group_ids).values('name')]


    def generate_default_groups(self):
        all_permissions = permission_manager.get_all_system_permissions()
        permission_code_to_permission_id = {p.codename: p.id for p in all_permissions}

        for group_name, permissions in DEFAULT_ROLES.items():
            permission_ids = [permission_code_to_permission_id[p.codename] for p in permissions]
            RolesManager.create(name=group_name, permissions=permission_ids)

roles_manager = RolesManager()

DEFAULT_ROLES = {
    "Admin" : permission_manager.ALL_PERMS,
    "Mentor" : [
        permission_manager.TRAINEE_CREATE,
        permission_manager.TRAINEE_EDIT,
        permission_manager.TRAINEE_VIEW,
        permission_manager.TRAINEE_DELETE,
        permission_manager.COURSES_CREATE,
        permission_manager.COURSES_EDIT,
        permission_manager.COURSES_VIEW,
        permission_manager.COURSES_DELETE,
    ],
    "Trainee": [
        permission_manager.COURSES_VIEW
    ]
}

class IsInGroup(BasePermission):
    def __init__(self, group_name):
        self.group_name = group_name

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            raise PermissionDenied(detail="You must be logged in to access this resource.")

        # Check if the user is an Admin
        if request.user.groups.filter(name="Admin").exists() or request.user.is_superuser:
            return True

        # Check if the user belongs to the required group
        if not request.user.groups.filter(name=self.group_name).exists():
            raise PermissionDenied(detail=f"You must be in the '{self.group_name}' group to access this resource.")
        return True
    