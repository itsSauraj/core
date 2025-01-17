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

    
class CourseDataSerializer(serializers.Serializer):
  course = CreateCourseRequestSerializer()
  modules = serializers.ListField(child=serializers.DictField())

  def validate_modules(self, value):
    if not value:
      raise serializers.ValidationError("Modules list cannot be empty.")
    for module in value:
      module_serializer = CreateModuleRequestSerializer(data=module)
      module_serializer.is_valid(raise_exception=True)
      lessons = module.get('lessons', [])
      if not lessons:
        raise serializers.ValidationError("Each module must have at least one lesson.")
      for lesson in lessons:
        lesson_serializer = CreateLessonRequestSerializer(data=lesson)
        lesson_serializer.is_valid(raise_exception=True)
    return value

  def validate(self, data):
    course_serializer = CreateCourseRequestSerializer(data=data['course'])
    course_serializer.is_valid(raise_exception=True)
    self.validate_modules(data['modules'])
    return data



# Respsonse serializers
class ResponseCourseSerializer(ModelSerializer):
  
  class Meta:
    model = Course
    fields = ['id', 'title', 'description']

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


## course group
from admin_panel.models import CourseCollection

class CreateRequestCourseGroupSerializer(ModelSerializer):
  image = serializers.ImageField(required=False)
  
  class Meta:
    model = CourseCollection
    fields = ['title', 'description', 'courses', 'image']

class ResponseCourseGroupSerializer(ModelSerializer):
  courses = serializers.SerializerMethodField()

  class Meta:
    model = CourseCollection
    fields = ['id', 'title', 'description', 'courses', 'image']

  def get_courses(self, obj):
    return [{'id': course.id, 'title': course.title} for course in obj.courses.all()]