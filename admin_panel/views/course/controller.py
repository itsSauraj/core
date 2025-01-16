from rest_framework import status
from rest_framework.response import Response

from django.core.exceptions import ObjectDoesNotExist

from rest_framework.permissions import IsAuthenticated
from admin_panel.roles_and_permissions.roles import IsInGroup

from admin_panel.services.course.serializer import CreateCourseRequestSerializer, CreateModuleRequestSerializer, \
                                              CreateLessonRequestSerializer, ResponseCourseSerializer, ResponseModuleSerializer
from admin_panel.services.course.service import CourseAPIService, CourseDataSerializer


from rest_framework.views import APIView


class CourseAPIView(APIView):

  def get_permissions(self):
    if self.request.method in ['POST', 'DELETE', 'PATCH']:
      return [IsAuthenticated(), IsInGroup('Admin')]
    else:
      return [IsAuthenticated()]

  def post(self, request):
    
    serializer = CourseDataSerializer(data=request.data)
    
    if not serializer.is_valid():
      return Response(serializer.errors, status=400)

    try:
      created_course = CourseAPIService.import_course(request, data=serializer.validated_data)
      return Response(ResponseCourseSerializer(created_course).data, status=201)
    except Exception as e:
      print(e)
      return Response({"message": "Internal Server Errr"}, status=500)


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
      course = CourseAPIService.get_course_structure(course_id, request.user) 
      return Response(course, status=200)
    
    courses = CourseAPIService.get_all_courses(created_by=request.user)
    courses_serializer = ResponseCourseSerializer(courses, many=True)
    
    context = courses_serializer.data
    
    return Response(context, status=200)
  

class ModuleAPIView(APIView):

  def get_permissions(self):
    if self.request.method in ['POST', 'DELETE', 'PATCH']:
      return [IsAuthenticated(), IsInGroup('Admin')]
    else:
      return [IsAuthenticated()]
    
  def post(self, request, course_id):

    if course_id is None:
      return Response({"message": "Course is required"}, status=400)
    
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

    if course_id is None or module_id is None:
      return Response({"message": "Course and Module is required"}, status=400)
    
    try:
      CourseAPIService.delete_module(request, course_id, module_id)
    except ObjectDoesNotExist:
      return Response({"message": "Module not found"}, status=404)
    
    return Response(status=status.HTTP_204_NO_CONTENT)
  

  def get(self, request, course_id, module_id=None):

    if module_id is not None:
      module = CourseAPIService.get_module_by_id(module_id)

      if module is None:
        return Response({"message": "Module not found"}, status=404)
      
      module_structure = CourseAPIService.get_all_module_contents(module) 

      return Response(module_structure, status=200)
    
    modules = CourseAPIService.get_course_modules(course_id)
    modules_serializer = ResponseModuleSerializer(modules, many=True)
    
    context = modules_serializer.data
    
    return Response(context, status=200)


class LessonAPIView(APIView):
  def get_permissions(self):
    if self.request.method in ['POST', 'DELETE', 'PATCH']:
      return [IsAuthenticated(), IsInGroup('Admin')]
    else:
      return [IsAuthenticated()]
    
  def post(self, request, course_id, module_id):

    if course_id is None or module_id is None:
      return Response({"message": "Course and Module is required"}, status=400)
    
    serializer = CreateLessonRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
      return Response(serializer.errors, status=400)
    
    created_module = CourseAPIService.create_lesson(request, course_id, module_id ,serializer.validated_data)
    
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
  

  def delete(self, request, course_id, module_id, lesson_id):

    if course_id is None or module_id is None or lesson_id is None:
      return Response({"message": "Course, Module and Lesson is required"}, status=400)
    
    try:
      CourseAPIService.delete_lesson(request, lesson_id)
    except ObjectDoesNotExist:
      return Response({"message": "Lesson not found"}, status=404)
    
    return Response(status=status.HTTP_204_NO_CONTENT)
