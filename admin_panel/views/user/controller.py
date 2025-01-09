from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from admin_panel.roles_and_permissions.roles import IsInGroup
from admin_panel.models import User

from admin_panel.services.user.serializer import CreateUserRequestSerializer, ResponseUserSerializer
from admin_panel.services.user.service import UserAPIService
from rest_framework_simplejwt.tokens import SlidingToken


class UserAPIView(APIView):
  """ Handles user creation, fetching, updating and deletion """
  def get_permissions(self):
    if self.request.method == 'POST':
        return [AllowAny()]
    else:
        return [IsAuthenticated()]

  def post(self, request):
    """ 
    Create a new user 
    data = {
      "first_name": "John",
      "last_name": "Doe",
      "email": "example@mail.com",
      "password": "password",
      "confirm_password": "password"
    }
    """
    serializer = CreateUserRequestSerializer(data=request.data)

    if not serializer.is_valid():
      return Response(serializer.errors, status=400)
    
    created_user = UserAPIService.create_admin(request, serializer.validated_data)
    user_serializer = ResponseUserSerializer(created_user)
    token = SlidingToken.for_user(user_serializer.instance)
    permissions = created_user.get_all_permissions()

    context = {
      "username": str(serializer.data.get('username')),
      "token": str(token),
      "permissions": permissions
    }
    
    return Response(context, status=201)

  
  def get(self, request):
    """ Fetch a user """
    return Response('Fetched user is working', status=200)

  
  def patch(self, request):
    """ Update a user """
    return Response("User Updaed", status=200)


  def delete(self, request):
    """ Delete a user """
    return Response(status=204)
  

class MemberAPIView(APIView):
  """ Handles mentor creation, fetching, updating and deletion """
  def get_permissions(self):
    if self.request.method in ['POST', 'DELETE']:
      return [IsAuthenticated(), IsInGroup('Admin')]
    else:
      return [IsAuthenticated(), IsInGroup('Mentor')]

  def post(self, request):
    """ 
    Create a new mentor 
    data = {
      "first_name": "John",
      "last_name": "Doe",
      "email": "",
      "password": "password",
      "confirm_password": "password"
      "role": "Mentor"
    }
    """

    serializer = CreateUserRequestSerializer(data=request.data)

    if not serializer.is_valid():
      return Response(serializer.errors, status=400)

    created_mentor = UserAPIService.create_sub_user(request, data=serializer.validated_data)

    context = {
      "id": created_mentor.id,
      "username": created_mentor.username,
      "email": created_mentor.email,
    }

    return Response(context, status=201)
  

  def get(self, request):
    """ Fetch a mentor """
    #TODO: Implement fetching of mentor

    context = {
      "user": request.user.username,
      "email": request.user.email,
      "permissions": request.user.get_all_permissions()
    }

    return Response(context, status=200)