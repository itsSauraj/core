from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group, Permission


class AuthModelBackend(ModelBackend):
    def get_all_permissions(self, user_obj, obj=None):
        return super().get_all_permissions(user_obj)