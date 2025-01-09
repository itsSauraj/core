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
        return [IsAuthenticated(), IsInGroup('Admin')]

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
    
    created_user = UserAPIService.create(request, serializer.validated_data, group="Admin")
    user_serializer = ResponseUserSerializer(created_user)
    token = SlidingToken.for_user(user_serializer.instance)
    permissions = created_user.get_all_permissions()

    context = {
      "username": user_serializer.data,
      "token": str(token),
      "permissions": permissions,
      "message": "User created successfully"
    }
    
    return Response(context, status=201)

  def get(self, request):
    """ Fetch a user """
    # TODO: Implement admin user fetching
    return Response('Fetched user is working', status=200)

  def patch(self, request):
    """ Update a user """
    # TODO: Implement admin user update
    return Response("User Updaed", status=200)

  def delete(self, request, id):
    """ Delete a user """
    if request.user.id != id:
      return Response("Cannot delete another user", status=403)
    
    try: 
      UserAPIService.delete(request, id)
    except User.DoesNotExist:
      return Response("Error deleting user", status=404)
    
    context = {
      "message": "User deleted successfully"
    }

    return Response(context, status=204)