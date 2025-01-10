from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from admin_panel.models import Course, CourseModules, CourseModuleLessons

class CreateCourseRequestSerializer(ModelSerializer):
  
  class Meta:
    model = Course
    fields = ['title', 'description']


class CreateModuleRequestSerializer(ModelSerializer):
  
  class Meta:
    model = CourseModules
    fields = ['title', 'description', 'parent_module', 'sequence']


class CreateLessonRequestSerializer(ModelSerializer):
  
  class Meta:
    model = CourseModuleLessons
    fields = ['title', 'description', 'course', 'module', 'sequence', 'duration']



# Respsonse serializers
class ResponseCourseSerializer(ModelSerializer):
  
  class Meta:
    model = Course
    fields = ['id', 'title', 'description', 'created_by', 'created_at']

class ResponseModuleSerializer(ModelSerializer):

  class Meta:
    model = CourseModules
    fields = ['id', 'title', 'description', 'course', 'parent_module', 'sequence', 'created_at']