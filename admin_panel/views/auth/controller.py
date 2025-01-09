from rest_framework_simplejwt.tokens import SlidingToken
from rest_framework_simplejwt.views import TokenObtainSlidingView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from admin_panel.models import User
from admin_panel.services.user.serializer import ResponseUserSerializer

class CustomTokenObtainSlidingView(TokenObtainSlidingView):
  permission_classes = [AllowAny]

  def post(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    try:
      serializer.is_valid(raise_exception=True)
    except Exception as e:
      return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.get(username=request.data['username'])
    token = SlidingToken.for_user(user)

    return Response({
      'token': str(token),
      'user': ResponseUserSerializer(user).data,
      'permissions': user.get_permissions()
    }, status=status.HTTP_200_OK)