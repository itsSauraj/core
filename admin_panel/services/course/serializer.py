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
    fields = ['title', 'description', 'sequence', 'duration']



# Respsonse serializers
class ResponseCourseSerializer(ModelSerializer):
  
  class Meta:
    model = Course
    fields = ['id', 'title', 'description', 'created_by', 'created_at']

class ResponseModuleSerializer(ModelSerializer):
  duration = serializers.DurationField(required=False)

  class Meta:
    model = CourseModules
    fields = ['id', 'title', 'description', 'course', 'parent_module', 'sequence', 'created_at', 'duration']

class ResponseModuleStructureSerializer(serializers.Serializer):
  metadata = serializers.SerializerMethodField()
  sub_modules = serializers.SerializerMethodField()
  lessons = serializers.SerializerMethodField()

  def get_metadata(self, obj):
    return ResponseModuleSerializer(obj['metadata']).data

  def get_sub_modules(self, obj):
    return ResponseModuleSerializer(obj['sub_modules'], many=True).data

  def get_lessons(self, obj):
    return ResponseModuleSerializer(obj['lessons'], many=True).data