from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import SlidingToken

from django.core.exceptions import ValidationError

from admin_panel.models import User
from admin_panel.services.user.serializer import ResponseUserSerializer
from admin_panel.services.user.profile_serializer import (
  UpdateUserRequestSerializer, 
  UpdatePasswordRequestSerializer
)
from admin_panel.services.user.profile_service import ProfileService

from rest_framework.permissions import IsAuthenticated

from admin_panel.services.user.profile_serializer import (
  ForgotPasswordSerializer,
  VerifyOTPSerializer,
  ResetPasswordSerializer
)


class ProfileAPIViewSet(viewsets.ModelViewSet):
  def get_permissions(self):
    if self.action in ['verify_account', 'forgot_password', 'verify_otp', 'reset_password']:
        return [AllowAny()]
    return [IsAuthenticated()]

  @action(detail=False, methods=['patch'], parser_classes=[FormParser, MultiPartParser])
  def update_profile(self, request):
    serializer = UpdateUserRequestSerializer(data=request.data, instance=request.user)
    
    if not serializer.is_valid():
      return Response(serializer.errors, status=400)
    
    try:
      updated_data = ProfileService.update_profile(request.user, serializer.validated_data)
      return Response(ResponseUserSerializer(updated_data).data, status=200)
    except Exception as e:
      return Response({"message": "Internal Server Error"}, status=500)
    
  @action(detail=False, methods=['patch'])
  def change_password(self, request):
    serializer = UpdatePasswordRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
      return Response(serializer.errors, status=400)
    
    try:
      if not request.user.check_password(serializer.validated_data['current_password']):
        return Response({"message": "Current password was incorrect"}, status=400)
      
      if serializer.validated_data['current_password'] == serializer.validated_data['new_password']:
        return Response({"message": "New password should be different from the current password"}, status=400)
      
      if serializer.validated_data['new_password'] != serializer.validated_data['confirm_password']:
        return Response({"message": "New password and confirm password do not match"}, status=400)
      
      ProfileService.change_password(request.user, serializer.validated_data['new_password'])
      return Response({"message": "Password updated successfully"}, status=200)
    except Exception as e:
      return Response({"message": "Internal Server Error"}, status=500)

  @action(detail=False, methods=['delete'])
  def delete_account(self, request):
    try:
      ProfileService.delete_account(request.user)
      return Response({"message": "Account deleted successfully"}, status=200)
    except Exception as e:
      return Response({"message": "Internal Server Error"}, status=500)
    
  @action(detail=False, methods=['post'])
  def verify_account(self, request):
    try:
      verified_user = ProfileService.verify_account(request.data['user_id'], request.data['otp'])
      user_serializer = ResponseUserSerializer(verified_user)
      if verified_user:
        context = {
          "token": str(SlidingToken.for_user(user_serializer.instance)),
          "user": user_serializer.data,
        }
        return Response(context, status=200)
      return Response({"message": "Invalid OTP"}, status=400)
    except Exception as e:
      return Response({"message": "Internal Server Error"}, status=500)

  @action(detail=False, methods=['post'])
  def forgot_password(self, request):
    serializer = ForgotPasswordSerializer(data=request.data)
    try:
      serializer.is_valid(raise_exception=True)
      
      result = ProfileService.forgot_password(
        email=serializer.validated_data['email']
      )

      if not result:
        raise User.DoesNotExist

      return Response({
        "message": "Password reset OTP sent to your email",
        "user_id": str(result.id),
        "username": str(result.username),
      }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
      return Response({
        "message": "No account found with this email address"
      }, status=status.HTTP_404_NOT_FOUND)
    except ValidationError as e:
      return Response({
        "message": str(e)
      }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
      print(e)
      return Response({
        "message": "Unable to process your request at this time"
      }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  @action(detail=False, methods=['post'])
  def verify_otp(self, request):
    serializer = VerifyOTPSerializer(data=request.data)
    try:
      serializer.is_valid(raise_exception=True)
      
      if not ProfileService.verify_otp(user_id=str(serializer.validated_data['user_id']), otp=str(serializer.validated_data['otp'])
      ): 
        raise Exception("Invalid or expired OTP")
      
      return Response({
        "message": "OTP verified successfully",
        "token": str(ProfileService.generate_password_reset_token(
          serializer.validated_data['user_id'])
        )
      }, status=status.HTTP_200_OK)
        
    except Exception as e:
      return Response({
        "message": "Invalid or expired OTP"
      }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
      return Response({
        "message": "Unable to verify OTP at this time"
      }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

  @action(detail=False, methods=['post'])
  def reset_password(self, request):
    serializer = ResetPasswordSerializer(data=request.data)
    try:
      serializer.is_valid(raise_exception=True)
      
      ProfileService.reset_password(
        token=serializer.validated_data['token'],
        new_password=serializer.validated_data['new_password']
      )
      
      return Response({
        "message": "Password has been reset successfully"
      }, status=status.HTTP_200_OK)
      
    except ValidationError as e:
      return Response({
        "message": str(e)
      }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
      return Response({
        "message": "Unable to reset password at this time"
      }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)