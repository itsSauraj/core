from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.tokens import SlidingToken

from admin_panel.roles_and_permissions.roles import IsInGroup
from admin_panel.models import User

from admin_panel.services.user.serializer import CreateUserRequestSerializer, ResponseUserSerializer
from admin_panel.services.user.service import UserAPIService


class UserAPIView(APIView):
  def get_permissions(self):
    if self.request.method == 'POST':
        return [AllowAny()]
    else:
        return [IsAuthenticated(), IsInGroup('Admin')]

  def post(self, request):
    serializer = CreateUserRequestSerializer(data=request.data)

    if not serializer.is_valid():
      return Response(serializer.errors, status=400)
    
    created_user = UserAPIService.create(request, serializer.validated_data, group="Admin")
    if created_user is False:
      return Response({"message": "User creation failed"}, status=400)
    user_serializer = ResponseUserSerializer(created_user)

    return Response(user_serializer.data, status=201)

  def delete(self, request, id):
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