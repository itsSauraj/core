from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from admin_panel.roles_and_permissions.roles import IsInGroup
from admin_panel.models import User

from admin_panel.services.user.serializer import CreateUserRequestSerializer, ResponseUserSerializer
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
      return [IsAuthenticated(), IsInGroup('Mentor')]

  def post(self, request):
    """ 
    Create a new mentor 
    data = {
      "employee_id": "123456",
      "first_name": "John",
      "last_name": "Doe",
      "email": "",
      "password": "password",
      "confirm_password": "password"
      "role": "Mentor",
      "joining_date": "2021-01-01",
      "phone_number": "1234567890",
    }
    """

    serializer = CreateUserRequestSerializer(data=request.data)

    if not serializer.is_valid():
      return Response(serializer.errors, status=400)

    group = serializer.validated_data.pop('role').capitalize()

    created_mentor = UserAPIService.create(request, data=serializer.validated_data, group=group)
    user_serializer = ResponseUserSerializer(created_mentor)

    return Response(user_serializer.data, status=201)

  def get(self, request, member_id):
    """ 
    Fetch a mentor 

    Example:
    GET /api/auth/user/member/uuid
    """

    try:
      member = UserAPIService.get_user_by_id(member_id)
    except User.DoesNotExist:
      return Response("User not found", status=404)

    context = ResponseUserSerializer(member).data

    return Response(context, status=200)

  def patch(self, request, member_id):
    """ 
    Update a mentor 

    Example:
    PATCH /api/auth/user/member/uuid
    """
    serializer = CreateUserRequestSerializer(data=request.data)

    if not serializer.is_valid():
      return Response(serializer.errors, status=400)

    try:
      member = UserAPIService.update(request, serializer.validated_data, member_id)
    except User.DoesNotExist:
      return Response("User not found", status=404)

    context = {
      "user": ResponseUserSerializer(member).data,
      "message": "User updated successfully"
    }

    return Response(context, status=200)

  def delete(self, request, member_id=None):
    """ 
    Delete a mentor 

    Example:
    DELETE /api/auth/user/member/uuid
    or
    Example:
    body = UUID[]
    eg: ["uuid1", "uuid2"]
    """
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
    """ 
    Fetch all mentors 

    Example:
    GET /api/user/mentor/
    """
    members = UserAPIService.get_user_mentors(request.user.id)
    context = ResponseUserSerializer(members, many=True).data
    return Response(context, status=200)
  
  @staticmethod
  @api_view(['GET'])
  @permission_required('custom_permission.trainees.view', raise_exception=True)
  def get_all_trainees(request):
    """ 
    Fetch all mentors 

    Example:
    GET /api/auth/user/trainee/
    """
    if request.user.groups.filter(name='Mentor').exists():
      #TODO: Add permission to fetch all trainees that are assigned to the mentor
      members = UserAPIService.get_all_trainees()
    else:
      members = UserAPIService.get_user_trainees(request.user.id)
    context = ResponseUserSerializer(members, many=True).data
    return Response(context, status=200)
  
  @staticmethod
  @api_view(['GET'])
  @permission_required('custom_permission.trainees.view', raise_exception=True)
  def generate_report(request, trainee_id):
    """ 
    Generate report for a mentor 

    Example:
    GET /api/auth/user/member/<uuid:trainee_id>/report
    """

    trainee = UserAPIService.get_trainee(trainee_id, request.user)

    if not trainee:
      return Response("Not trainee not found", status=404)

    enrolled_courses_collection = trainee.enrolled_courses.all()

    enrolled_collections_data = AdminReportCourseCollectionSerializer(enrolled_courses_collection, many=True).data
    
    serializer_context = {
      "user": request.user,
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