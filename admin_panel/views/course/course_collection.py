import json

from rest_framework import status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser

from django.core.exceptions import ObjectDoesNotExist

from rest_framework.permissions import IsAuthenticated
from admin_panel.roles_and_permissions.roles import IsInGroup

from admin_panel.services.course.serializer import CreateRequestCourseGroupSerializer, ResponseCourseGroupSerializer
from admin_panel.services.course.course_collection import CourseCollectionAPIService


from rest_framework.views import APIView

class CourseCollectionAPIView(APIView):
  parser_classes = [MultiPartParser, FormParser] 

  def get_permissions(self):
    if self.request.method in ['POST', 'DELETE', 'PATCH']:
      return [IsAuthenticated(), IsInGroup('Admin')]
    else:
      return [IsAuthenticated()]

  def post(self, request):

    serializer = CreateRequestCourseGroupSerializer(data=request.data)
    
    if not serializer.is_valid():
      return Response(serializer.errors, status=400)

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
        ids = request.data.get("ids")
        if not ids:
          return Response({"message": "Collection ID(s) required"}, status=400)
        CourseCollectionAPIService.delete(request, ids, many=True)
      return Response({"message": "Course(s) deleted successfully"}, status=204)
    except ObjectDoesNotExist:
      return Response({"message": "Course not found"}, status=404)

  
  def patch(self, request, collection_id=None):
    try:
      course_collection = CourseCollectionAPIService.get(request.user, collection_id)
      serializer = CreateRequestCourseGroupSerializer(course_collection, data=request.data, partial=True)
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
