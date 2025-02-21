import json

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated

from django.core.exceptions import ObjectDoesNotExist

from admin_panel.roles_and_permissions.roles import IsInGroup
from admin_panel.roles_and_permissions.decorators import group_required

from admin_panel.services.course.serializer import CreateRequestCourseGroupSerializer, \
  UpdateRequestCourseGroupSerializer, ResponseCourseGroupSerializer
from admin_panel.services.course.course_collection import CourseCollectionAPIService


from rest_framework.views import APIView

class CourseCollectionAPIView(APIView):
  def get_parsers(self):
    if self.request.method == 'POST':
      return [MultiPartParser(), FormParser()]
    return super().get_parsers()

  def get_permissions(self):
    if self.request.method in ['POST', 'DELETE', 'PATCH', 'PUT']:
      return [IsAuthenticated(), IsInGroup('Admin')]
    else:
      return [IsAuthenticated()]

  def post(self, request):

    serializer = CreateRequestCourseGroupSerializer(data=request.data)
    courses_data = json.loads(request.data.get('courses'))
    
    if not serializer.is_valid():
      return Response(serializer.errors, status=400)

    courses_data = [str(uuid) for uuid in courses_data]
    serializer.validated_data['courses'] = courses_data

    try:
      created_course = CourseCollectionAPIService.create(request, data=serializer.validated_data)
      return Response(ResponseCourseGroupSerializer(created_course).data, status=201)
    except Exception as e:
      print(e)
      return Response({"message": "Internal Server Errr"}, status=500)


  def delete(self, request, collection_id=None):
    try:
      if collection_id:
        CourseCollectionAPIService.delete(request, collection_id)
      else:
        ids = request.data
        if not ids:
          return Response({"message": "Collection ID(s) required"}, status=400)
        CourseCollectionAPIService.delete(request, ids, many=True)
      return Response({"message": "Course(s) deleted successfully"}, status=204)
    except ObjectDoesNotExist:
      return Response({"message": "Course not found"}, status=404)

  
  def patch(self, request, collection_id=None):
    try:
      course_collection = CourseCollectionAPIService.get(request.user, collection_id)
      if not course_collection:
        return Response({"message": "Course not found"}, status=404)
      serializer = UpdateRequestCourseGroupSerializer(course_collection, data=request.data, partial=True)

      if 'courses' in request.data:
        courses_data = json.loads(request.data.get('courses'))
        serializer.is_valid(raise_exception=True)
        courses_data = [str(uuid) for uuid in courses_data]
        previous_courses = [course.id for course in course_collection.courses.all()]
        updated_courses = previous_courses + courses_data
        serializer.validated_data['courses'] = updated_courses

      if not serializer.is_valid():
        return Response(serializer.errors, status=400)
      course_collection = CourseCollectionAPIService.update(request, course_collection, serializer.validated_data)
      return Response(ResponseCourseGroupSerializer(course_collection).data, status=200)
    except ObjectDoesNotExist:
      return Response({"message": "Course not found"}, status=404)


  def get(self, request, collection_id=None):

    if collection_id is not None:
      course_collection = CourseCollectionAPIService.get(request.user, collection_id) 
      return Response(ResponseCourseGroupSerializer(course_collection).data, status=200)
    
    course_collections = CourseCollectionAPIService.get_all(request.user)
    courses_serializer = ResponseCourseGroupSerializer(course_collections, many=True)
    
    context = courses_serializer.data
    
    return Response(context, status=200)


class CourseCollectionModules():

  @staticmethod
  @api_view(['DELETE', 'PATCH'])
  @group_required('Admin')
  def course_actions_collection(request, collection_id, course_id):

    print(request.method)

    if request.method == 'DELETE':
      return CourseCollectionModules.delete_course_from_collection(request, collection_id, course_id)

  @staticmethod
  def delete_course_from_collection(request, collection_id, course_id):
    try:
      CourseCollectionAPIService.delete_course_from_collection(request, collection_id, course_id)
      return Response({"message": "Course deleted from collection successfully"}, status=204)
    except ObjectDoesNotExist:
      return Response({"message": "Course not found"}, status=404)
    

  @staticmethod
  def all_courses_in_collection(request, collection_id):

    try:
      courses = CourseCollectionAPIService.get_all_courses_in_collection(request, collection_id)
      return Response(courses, status=200)
    except ObjectDoesNotExist:
      return Response({"message": "Course not found"}, status=404)
  
  @staticmethod
  @api_view(['PUT'])
  @group_required('Admin')
  def set_default_collection(request, collection_id):
    if not collection_id:
      return Response({"message": "Collection ID is required"}, status=400)
    
    collection = CourseCollectionAPIService.get(request.user, collection_id)

    if not collection:
      return Response({"message": "Collection not found"}, status=404)
    
    CourseCollectionAPIService.set_default_collection(request, collection)

    return Response({"message": "Collection set as default"}, status=200)