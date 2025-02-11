from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated

from admin_panel.services.user.serializer import ResponseUserSerializer
from admin_panel.services.user.profile_serializer import UpdateUserRequestSerializer, UpdatePasswordRequestSerializer
from admin_panel.services.user.profile_service import ProfileService

from rest_framework.permissions import IsAuthenticated


class ProfileAPIViewSet(viewsets.ModelViewSet):
  def get_permissions(self):
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
      if ProfileService.verify_account(request.data['user_id'], request.data['otp']):
        return Response({"message": "Account verified successfully"}, status=200)
      return Response({"message": "Invalid OTP"}, status=400)
    except Exception as e:
      return Response({"message": "Internal Server Error"}, status=500)