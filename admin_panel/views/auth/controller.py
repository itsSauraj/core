from rest_framework_simplejwt.tokens import SlidingToken
from rest_framework_simplejwt.views import TokenObtainSlidingView, TokenRefreshSlidingView, TokenViewBase
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from rest_framework.views import APIView

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

class CustomTokenRefreshSlidingView(TokenRefreshSlidingView):
    def post(self, request, *args, **kwargs):
        
        print(f"Request data: {request.data}")

        try:
            response = super().post(request, *args, **kwargs)
            return response

        except TokenError as e:
            return Response(
                {"message": "Token has been expired"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return Response(
                {"message": "An unexpected error occurred"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
class LogoutView(TokenViewBase):
    """
    This view handles logging out by blacklisting the refresh token.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            token = request.data.get('token', None)            
            if token is None:
                return Response(
                    {"message": "Token is required to logout."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = SlidingToken(token)
            token.blacklist()
            
            return Response(
                {"message": "Successfully logged out."},
                status=status.HTTP_205_RESET_CONTENT
            )

        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
