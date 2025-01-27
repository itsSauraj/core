from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from admin_panel.models import Course, CourseCollection, UserCoursesEnrolled, \
  UserCourseProgress, UserCourseActivity
from admin_panel.services.course.serializer import ResponseCourseGroupSerializer
from admin_panel.services.trainee.service import TraineeCourseServices


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
  
class DeleteUserCollectionSerializer(serializers.Serializer):
  user = serializers.UUIDField()
  collection = serializers.ListField(child=serializers.UUIDField())


class ReportCourseCollectionSerializer(ModelSerializer):
  collection = serializers.SerializerMethodField()
  progress = serializers.SerializerMethodField()
  days_taken = serializers.SerializerMethodField()
  due_time = serializers.SerializerMethodField()
  estimated_completion_date = serializers.SerializerMethodField()

  class Meta:
    model = UserCoursesEnrolled
    fields = ['started_on', 'completed_on', 'is_completed', 'progress', 'days_taken', 
              'due_time', 'estimated_completion_date' ,'assigned_by', 'collection']

  def get_collection(self, obj):
    return ResponseCourseGroupSerializer(obj.collection).data
  
  def get_progress(self, obj):
    return TraineeCourseServices.get_collection_progress(obj)
  
  def get_days_taken(self, obj):
    return TraineeCourseServices.get_time_taken_to_complete(obj)
  
  def get_due_time(self, obj):
    due_days = TraineeCourseServices.get_time_taken_to_complete(obj) - obj.collection.alloted_time
    return due_days
  
  def get_estimated_completion_date(self, obj):
    return TraineeCourseServices.estimated_collection_completeion_date(obj)

  def assigned_by(self, obj):
    return obj.collection.created_by.username

class ResponseTraineeAssignedCollectionsMinifiedSerializer(ModelSerializer):
  title = serializers.SerializerMethodField()
  id = serializers.SerializerMethodField()

  class Meta:
    model = UserCoursesEnrolled
    fields = ['id', 'title']

  def get_title(self, obj):
    return obj.collection.title
  
  def get_id(self, obj):
    return obj.collection.id
  
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
  
class LessonLearnedSerializer(serializers.Serializer):
  collection_id = serializers.UUIDField()
  course_id = serializers.UUIDField()
  lesson_id = serializers.UUIDField()