from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from admin_panel.models import Course, CourseCollection, UserCoursesEnrolled, UserCourseProgress, UserCourseActivity
from admin_panel.services.course.serializer import ResponseCourseGroupSerializer


class CreateUserCollectionSerializer(ModelSerializer):
  collection = serializers.ListField(child=serializers.UUIDField(), required=False)
  course = serializers.ListField(child=serializers.UUIDField(), required=False)

  class Meta:
    model = UserCoursesEnrolled
    fields = ['course', 'collection', 'user']
  
  def validate_collection(self, value):

    if isinstance(value, (list, tuple)):
      collections = CourseCollection.objects.filter(id__in=value)
      if collections.count() != len(value):
        raise serializers.ValidationError("One or more collection IDs are invalid")
      return collections
    return value
  

class ReportCourseCollectionSerializer(ModelSerializer):
  collection = serializers.SerializerMethodField()

  class Meta:
    model = UserCoursesEnrolled
    fields = ['collection', 'started_on', 'completed_on', 'is_completed', 'assigned_by']

  def get_collection(self, obj):
    return ResponseCourseGroupSerializer(obj.collection).data
  
  def assigned_by(self, obj):
    return obj.collection.created_by.username

class ResponseTraineeAssignedCollections(ModelSerializer):
  collection = serializers.SerializerMethodField()

  class Meta:
    model = UserCoursesEnrolled
    fields = ['collection', 'started_on', 'completed_on', 'completed']

  def get_collection(self, obj):
    return ResponseCourseGroupSerializer(obj.collection).data


class CreateUserCourseActivitySerializer(ModelSerializer):
  class Meta:
    model = UserCourseActivity
    fields = ['user', 'course']


class CreateUserCourseProgressSerializer(ModelSerializer):
  class Meta:
    model = UserCourseProgress
    fields = ['user', 'course', 'module', 'lesson']

class CreateLessonProgressSerializer(ModelSerializer):
  class Meta:
    model = UserCourseProgress
    fields = ['user', 'course', 'module', 'lesson']

class ResponeUserCourseProgressSerializer(ModelSerializer):
  class Meta:
    model = UserCourseProgress
    fields = ['lesson']

  def get_lesson(self, obj):
    return obj.lesson.id