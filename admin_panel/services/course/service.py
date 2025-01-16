from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response

from admin_panel.models import Course, CourseModules, CourseModuleLessons

from .serializer import ResponseCourseSerializer, ResponseModuleStructureSerializer, \
  CreateLessonRequestSerializer, CreateModuleRequestSerializer, CourseDataSerializer

from .dependencies import get_course_duration, get_module_duration, get_all_module_contents

class CourseAPIService:

  @staticmethod
  def get_course_by_id(course_id, created_by=None):
    try:
      course = Course.objects.get(id=course_id, created_by=created_by)
      return course
    except ObjectDoesNotExist:
      return None
        
  @staticmethod
  def get_all_courses(created_by=None):
    return Course.objects.all().filter(created_by=created_by)
  
  @staticmethod
  def get_module_by_id(module_id):
    try:
      module = CourseModules.objects.get(id=module_id)
      return module
    except ObjectDoesNotExist:
      return None


  @staticmethod
  def get_course_modules(course_id, module_id=None):
    modules = CourseModules.objects.all().filter(course=course_id).filter(parent_module__id=module_id)
    for module in modules:
      module.duration = get_module_duration(module)
    return modules
  
  @staticmethod
  def get_all_module_contents(module):
    sub_modules = module.get_sub_modules
    lessons = module.get_all_lessons

    module.duration = get_module_duration(module)
    for sub_module in sub_modules:
      sub_module.duration = get_module_duration(sub_module)

    module_structure = {
      'metadata': module,
      'sub_modules': sub_modules,
      'lessons': lessons
    }

    serializer_data = ResponseModuleStructureSerializer(module_structure).data
    return serializer_data
  
      
  @staticmethod
  def get_all_module_contents_recursive(module):
    module_structure = {
      'metadata': None,
      'sub_modules': [],
      'lessons': []
    }

    module_data = CreateModuleRequestSerializer(module).data
    module_data['duration'] = get_module_duration(module)
    module_structure['metadata'] = module_data
    #lessson
    module_structure['lessons'] = CreateLessonRequestSerializer(module.get_all_lessons, many=True).data

    #sub modules
    sub_modules = module.get_sub_modules
    if sub_modules.count() > 0:
      for sub_module in sub_modules:
        module_structure['sub_modules'].append(CourseAPIService.get_all_module_contents_recursive(sub_module))

    return module_structure
  

  @staticmethod
  def import_course(request, data):
    course = CourseAPIService.create(request, data['course'])

    for module in data['modules']:
      module['course'] = course
      created_module = CourseAPIService.create_module(request, course.id, CreateModuleRequestSerializer(module).data)

      for lesson in module.get('lessons', []):
        lesson['module'] = created_module
        hours, minutes, seconds = map(int, lesson['duration'].split(':'))
        lesson['duration'] = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        CourseAPIService.create_lesson(request, course.id, created_module.id, CreateLessonRequestSerializer(lesson).data)

    return course


  @staticmethod
  def create(request, data):
    course = Course.objects.create(**data)
    course.created_by = request.user
    course.save()
    return course
  
  @staticmethod
  def delete(request, course_id):
    course = CourseAPIService.get_course_by_id(course_id, request.user)
    course.delete()

  @staticmethod
  def update(request, course_id, data):
    course = CourseAPIService.get_course_by_id(course_id, request.user)

    for key, value in data.items():
      setattr(course, key, value)

    course.save()

    return course

  @staticmethod
  def create_module(request, course_id, data):

    course = CourseAPIService.get_course_by_id(course_id, request.user)

    if course is None:
      return None

    module = CourseModules(**data, course=course)
    module.save()
    return module
  
  @staticmethod
  def delete_module(request, course_id, module_id):
    module = CourseModules.objects.get(id=module_id)
    module.delete()
  

  @staticmethod
  def create_lesson(request, course_id, module_id, data):
    course = CourseAPIService.get_course_by_id(course_id, request.user)
    module = CourseAPIService.get_module_by_id(module_id)

    if course is None or module is None:
      return None

    lesson = CourseModuleLessons(**data, course=course, module=module)
    lesson.save()
    return lesson

  @staticmethod
  def delete_lesson(request, lesson_id):
    lesson = CourseModuleLessons.objects.get(id=lesson_id)
    lesson.delete()


  @staticmethod
  def get_course_structure(course_id, user):
    course = CourseAPIService.get_course_by_id(course_id, user)
    metadata = ResponseCourseSerializer(course).data
    metadata['duration'] = get_course_duration(course)

    modules = course.get_all_modules()
    module_structure = []
    
    for module in modules:
      module_structure.append(CourseAPIService.get_all_module_contents_recursive(module))

    return {
      "metadata": metadata,
      "modules": module_structure,
    }