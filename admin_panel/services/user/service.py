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
  def get_created_courses(user_id):
    return UserAPIService.get_user_by_id(user_id).get_created_courses()
  

  @staticmethod
  def create_admin(request, data):

    serializer = UserSerializer(data)

    user, created = User.objects.get_or_create(
      **serializer.data,
      is_staff=True,
    )

    admin_group = Group.objects.get(name='Admin')
    if created:
      user.set_password(serializer.data['password'])
      user.groups.add(admin_group)
      user.save()
      
    return user

  @staticmethod
  @permission_required(['custom_permission.mentors.create', 'custom_permission.trainees.create'], raise_exception=True)
  def create_sub_user(request, data):
    
    is_staff = False
    type = data.get('role').capitalize()
    
    serializer = UserSerializer(data)
    
    if type in ['Mentor', 'Admin']:
      is_staff = True

    user, created = User.objects.get_or_create(
      **serializer.data,
      is_staff=is_staff,
    )

    user_group = Group.objects.get(name=type)
    if created:
      user.created_by = request.user
      user.set_password(serializer.data['password'])
      user.groups.add(user_group)
      user.save()

    return user
