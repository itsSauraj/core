from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from admin_panel.models import Course, CourseModules, CourseModuleLessons, CourseCollection,\
    UserCourseProgress
from .dependencies import get_course_duration, get_collection_duration, get_module_duration

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
    fields = ['id', 'title', 'description', 'sequence', 'duration']

    
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
  duration = serializers.SerializerMethodField()
  
  class Meta:
    model = Course
    fields = ['id', 'title', 'description', 'duration']

  def get_duration(self, obj):
    return get_course_duration(obj)

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


class UUIDSerializer(serializers.Serializer):
  uuids = serializers.ListField(child=serializers.UUIDField())

class CreateRequestCourseGroupSerializer(ModelSerializer):
  image = serializers.ImageField(required=False)
  
  class Meta:
    model = CourseCollection
    fields = ['title', 'description', 'image', 'alloted_time']

class ResponseCourseGroupSerializer(ModelSerializer):
  courses = serializers.SerializerMethodField()
  duration = serializers.SerializerMethodField()
  is_default = serializers.SerializerMethodField()

  class Meta:
    model = CourseCollection
    fields = ['id', 'title', 'description', 'duration', 'image', 'alloted_time', 'courses', 'is_default']

  def get_courses(self, obj):
    return [
      {
        'id': course.id, 
        'title': course.title,
        'description': course.description,
        'duration': get_course_duration(course)
      } for course in obj.courses.all()
    ]
  
  def get_duration(self, obj):
    return get_collection_duration(obj)
  
  def get_is_default(self, obj):
    return obj.is_default
  

class ResponseReportModuleSerializer(serializers.ModelSerializer):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.user_id = self.context.get('user_id')

  duration = serializers.SerializerMethodField()
  lessons = serializers.SerializerMethodField()
  
  class Meta:
    model = CourseModules
    fields = ['id', 'title', 'description', 'sequence', 'duration', 'lessons']

  def get_duration(self, obj):
    return get_module_duration(obj)

  def get_lessons(self, obj):
    return ResponseCompletedLessonsSerializer(obj.get_all_lessons, 
                                              context={'user_id': self.user_id}, many=True).data
  
class ResponseCompletedLessonsSerializer(serializers.ModelSerializer):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.user_id = self.context.get('user_id')
  
  # UserCourseProgress
  completed = serializers.SerializerMethodField()
  completed_on = serializers.SerializerMethodField()

  class Meta:
    model = CourseModuleLessons
    fields = ['id', 'title', 'description', 'sequence', 'duration', 'completed', 'completed_on']

  def get_completed(self, obj):
    return UserCourseProgress.objects.filter(user_id=self.user_id, lesson_id=obj.id).exists()
  
  def get_completed_on(self, obj):
    completed_lesson = UserCourseProgress.objects.filter(user_id=self.user_id, lesson_id=obj.id).first()
    return completed_lesson.completed_on if completed_lesson else None
  

class ResponseCollectionsMinifiedSerializer(ModelSerializer):
  title = serializers.SerializerMethodField()
  id = serializers.SerializerMethodField()

  class Meta:
    model = CourseCollection
    fields = ['id', 'title']

  def get_title(self, obj):
    return obj.title

  def get_id(self, obj):
    return obj.id