from admin_panel.models import User
from admin_panel.services.user.serializer import UserSerializer

from django.contrib.auth.decorators import permission_required
from django.contrib.auth.models import Group

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

class UserAPIService:

  @staticmethod
  def get_user_by_id(id):
    return User.objects.get(id=id)
  
  @staticmethod
  def get_user_by_email(email):
    return User.objects.get(email=email)
  
  @staticmethod
  def get_user_by_username(username):
    return User.objects.get(username=username)
  
  @staticmethod
  def get_user_mentors(user_id):
    return UserAPIService.get_user_by_id(user_id).get_created_mentors()
  
  @staticmethod
  def get_user_trainees(user_id):
    return UserAPIService.get_user_by_id(user_id).get_created_trainees()
  
  @staticmethod
  def get_all_trainees():
    return User.objects.filter(groups__name='Trainee')
  
  @staticmethod
  def get_created_courses(user_id):
    return UserAPIService.get_user_by_id(user_id).get_created_courses()
  
  @staticmethod
  def add_user_to_group(user, group, many=False):
    if many:
      for group_name in group:
        user.groups.add(Group.objects.get(name=group_name))
    else:
      user.groups.add(Group.objects.get(name=group))
    user.save()

  @staticmethod
  def create(request, data, group=[]):

    user_permissions = request.user.get_all_permissions()
    required_permissions = ['custom_permission.mentors.create', 'custom_permission.trainees.create']

    serializer = UserSerializer(data)

    if 'Admin' not in group and not all(permission in user_permissions for permission in required_permissions):
        raise PermissionError('You do not have permission to create a user')

    user = User.objects.create_user(**serializer.data)
    UserAPIService.add_user_to_group(user, group)

    if 'Admin' not in group:
      user.created_by = request.user
      user.save()
      
    return user
  
  @staticmethod
  def update(request, data, user_id):

    user = UserAPIService.get_user_by_id(user_id)
    serializer = UserSerializer(data)

    if user != request.user and 'Admin' not in request.user.groups.all():
      raise PermissionError('You do not have permission to update this user')

    for key, value in serializer.data.items():
      setattr(user, key, value)
    user.save()

    return user

  @staticmethod
  def delete(request, user_id, many=False):
    if many:
      User.objects.filter(id__in=user_id).delete()
    else:
      UserAPIService.get_user_by_id(user_id).delete()

    return True