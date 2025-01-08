from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from admin_panel.roles_and_permissions.roles import IsInGroup
from admin_panel.models import User

from admin_panel.services.user.serializer import CreateAdminRequestSerializer, UserSerializer
from admin_panel.services.user.service import UserAPIService


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
    serializer = CreateAdminRequestSerializer(data=request.data)

    if serializer.is_valid():
      context = UserAPIService.create_admin(request, serializer.validated_data)
      serializer = UserSerializer(context)
    else:
      return Response(serializer.errors, status=400)
    return Response(serializer.data, status=201)

  
  def get(self, request):
    """ Fetch a user """
    return Response('Fetched user is working', status=200)

  
  def patch(self, request):
    """ Update a user """
    return Response("User Updaed", status=200)


  def delete(self, request):
    """ Delete a user """
    return Response(status=204)
  

class MentorAPIView(APIView):
  """ Handles mentor creation, fetching, updating and deletion """
  def get_permissions(self):
    if self.request.method == 'POST' or self.request.method == 'DELETE':
      return [IsAuthenticated, lambda: IsInGroup('Admin')]
    else:
      return [IsAuthenticated, lambda: IsInGroup('Mentor')]

  def post(self, request):
    """ 
    Create a new mentor 
    data = {
      "first_name": "John",
      "last_name": "Doe",
      "email": "",
      "password": "password",
      "confirm_password": "password"
    }
    """
    UserAPIService.create_mentor(request, request.data)
    return Response("Is Authenticated", status=201)
  

  def get(self, request):
    """ Fetch a mentor """

    context = {
      "user": request.user.username,
      "email": request.user.email,
    }

    return Response(context, status=200)