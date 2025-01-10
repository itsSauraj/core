from rest_framework import status
from rest_framework.response import Response

from django.core.exceptions import ObjectDoesNotExist

from rest_framework.permissions import IsAuthenticated
from admin_panel.roles_and_permissions.roles import IsInGroup

from admin_panel.services.course.serializer import CreateCourseRequestSerializer, CreateModuleRequestSerializer, \
                                              CreateLessonRequestSerializer, ResponseCourseSerializer, ResponseModuleSerializer
from admin_panel.services.course.service import CourseAPIService


from rest_framework.views import APIView


class CourseAPIView(APIView):

  def ger_permissions(self):
    if self.request.method in ['POST', 'DELETE', 'PATCH']:
      return [IsAuthenticated(), IsInGroup('Admin')]
    else:
      return [IsAuthenticated()]

  def post(self, request):
    
    serializer = CreateCourseRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
      return Response(serializer.errors, status=400)
    
    created_course = CourseAPIService.create(request, data=serializer.validated_data)
    course_serializer = ResponseCourseSerializer(created_course)
    
    context = {
      "course": course_serializer.data,
      "message": "Course created successfully"
    }
    
    return Response(context, status=201)

  def delete(self, request, course_id=None):

    if course_id is None:
      return Response({"message": "Course ID is required"}, status=400)

    try:
      CourseAPIService.delete(request, course_id)
    except ObjectDoesNotExist:
      return Response({"message": "Course not found"}, status=404)

    return Response(status=status.HTTP_204_NO_CONTENT)
  
  def patch(self, request, course_id=None):

    if course_id is None:
      return Response({"message": "Course ID is required"}, status=400)
    
    serializer = CreateCourseRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
      return Response(serializer.errors, status=400)
    
    try:
      updated_course = CourseAPIService.update(request, course_id, serializer.validated_data)
    except ObjectDoesNotExist:
      return Response({"message": "Course not found"}, status=404)

    course_serializer = ResponseCourseSerializer(updated_course)
    
    context = {
      "course": course_serializer.data,
      "message": "Course updated successfully"
    }
    
    return Response(context, status=200)
  
  def get(self, request, course_id=None):

    if course_id is not None:
      course = CourseAPIService.get_course_by_id(course_id, request.user)
      
      context = {
        "course": ResponseCourseSerializer(course).data
      }
      
      return Response(context, status=200)
    
    courses = CourseAPIService.get_all_courses(created_by=request.user)
    courses_serializer = ResponseCourseSerializer(courses, many=True)
    
    context = courses_serializer.data
    
    return Response(context, status=200)
  

class ModuleAPIView(APIView):

  def ger_permissions(self):
    if self.request.method in ['POST', 'DELETE', 'PATCH']:
      return [IsAuthenticated(), IsInGroup('Admin')]
    else:
      return [IsAuthenticated()]
    
  def post(self, request, course_id):

    if course_id is None:
      return Response({"message": "Course ID is required"}, status=400)
    
    serializer = CreateModuleRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
      return Response(serializer.errors, status=400)
    
    created_module = CourseAPIService.create_module(request, course_id, serializer.validated_data)
    
    context = {
      "module": ResponseModuleSerializer(created_module).data,
      "message": "Module created successfully"
    }

    if created_module is None:

      context = {
        "message": "Something went wrong"
      }

      return Response(context, status=500)
    
    return Response(context, status=201)
  

  def delete(self, request, course_id, module_id):
    
    try:
      CourseAPIService.delete_module(course_id, module_id)
    except ObjectDoesNotExist:
      return Response({"message": "Module not found"}, status=404)
    
    return Response(status=status.HTTP_204_NO_CONTENT)
