from admin_panel.models import User
from admin_panel.services.user.serializer import UserSerializer

from django.contrib.auth.models import Group

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken

class UserAPIService:

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

  def create_mentor(request, data):
    print("Creating mentor")
    return { 'message': 'Mentor created' }
