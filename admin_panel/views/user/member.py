from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from admin_panel.roles_and_permissions.roles import IsInGroup
from admin_panel.models import User

from admin_panel.services.user.serializer import CreateUserRequestSerializer, UpdateUserRequestSerializer, \
  ResponseUserSerializer
from admin_panel.services.user.service import UserAPIService
from admin_panel.services.course.service import CourseAPIService
from admin_panel.services.trainee.admin_serializer import AdminReportCourseCollectionSerializer, \
  AdminResponseCourseGroupSerializer
from admin_panel.services.trainee.service import TraineeCourseServices

from django.contrib.auth.decorators import permission_required
from admin_panel.roles_and_permissions.decorators import group_required


class MemberAPIView(APIView):
  """ Handles mentor creation, fetching, updating and deletion """
  def get_permissions(self):
    if self.request.method in ['POST', 'DELETE']:
      return [IsAuthenticated(), IsInGroup('Admin')]
    else:
      return [IsAuthenticated()]

  def post(self, request):
    serializer = CreateUserRequestSerializer(data=request.data)

    if not serializer.is_valid():
      return Response(serializer.errors, status=400)

    group = serializer.validated_data.pop('role').capitalize()

    created_mentor = UserAPIService.create(request, data=serializer.validated_data, group=group)
    user_serializer = ResponseUserSerializer(created_mentor)

    return Response(user_serializer.data, status=201)

  def get(self, request, member_id):
    try:
      member = UserAPIService.get_user_by_id(member_id)
    except User.DoesNotExist:
      return Response("User not found", status=404)

    context = ResponseUserSerializer(member).data

    return Response(context, status=200)

  def patch(self, request, member_id=None):
    if not member_id:
      return Response("User ID is required", status=400)
    
    if member_id != request.user.id and 'Admin' not in [group.name for group in list(request.user.groups.all())]:
      return Response("You are not authorized to perform this action", status=403)
    
    unchanged_data = UserAPIService.remove_dublicate_values(member_id, request.data)
    if unchanged_data == {}:
      return Response("No data to update", status=400)

    serializer = UpdateUserRequestSerializer(data=unchanged_data, partial=True)

    if not serializer.is_valid():
      return Response(serializer.errors, status=400)

    try:
      member = UserAPIService.update(request, serializer.validated_data, member_id)
    except User.DoesNotExist:
      return Response("User not found", status=404)

    return Response(ResponseUserSerializer(member).data, status=200)

  def delete(self, request, member_id=None):
    if not member_id and not request.data:
      return Response("User ID is required", status=400)

    try:
      if member_id:
        UserAPIService.delete(request, member_id)
        message = "User deleted successfully"
      else:
        UserAPIService.delete(request, request.data, many=True)
        message = "Users deleted successfully"
      return Response({"message": message}, status=204)
    except User.DoesNotExist:
      return Response("User not found" if member_id else "One or more users not found", status=404)
    

class MemberModules():
  
  @staticmethod
  @api_view(['GET'])
  @permission_required('custom_permission.mentors.view', raise_exception=True)
  def get_all_mentors(request):
    members = UserAPIService.get_user_mentors(request.user.id)
    context = ResponseUserSerializer(members, many=True).data
    return Response(context, status=200)
  
  @staticmethod
  @api_view(['GET'])
  @permission_required('custom_permission.trainees.view', raise_exception=True)
  def get_all_trainees(request):

    if request.user.groups.filter(name='Mentor').exists():
      members = UserAPIService.get_all_trainees()
    else:
      members = UserAPIService.get_user_trainees(request.user.id)
    context = ResponseUserSerializer(members, many=True).data
    return Response(context, status=200)
  
  @staticmethod
  @api_view(['GET'])
  @permission_required('custom_permission.trainees.view', raise_exception=True)
  def generate_report(request, trainee_id):
    if request.user.groups.filter(name='Trainee').exists():
      trainee = request.user
    else:
      trainee = UserAPIService.get_trainee(trainee_id, request.user)

    if not trainee:
      return Response("Not trainee not found", status=404)

    enrolled_courses_collection = trainee.enrolled_courses.all()

    enrolled_collections_data = AdminReportCourseCollectionSerializer(enrolled_courses_collection, many=True).data
    
    serializer_context = {
      "trainee_id": trainee_id,
      "metadata": enrolled_collections_data
    }
    
    collection_data_list = [
      AdminResponseCourseGroupSerializer(enrolled_collection.collection, context=serializer_context).data 
      for enrolled_collection in enrolled_courses_collection
    ]

    context = {
      'trainee': ResponseUserSerializer(trainee).data,
      'collections':  collection_data_list
    }
    return Response(context, status=200)