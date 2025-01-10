from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response

from admin_panel.models import Course, CourseModules, CourseModuleLessons

from admin_panel.services.course.serializer import CreateCourseRequestSerializer, CreateLessonRequestSerializer, \
                                  CreateModuleRequestSerializer


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
  def create(request, data):
    course, created = Course.objects.get_or_create(**data)

    if not created:
      return None
    
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