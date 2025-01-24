from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from admin_panel.models import CourseCollection, UserCoursesEnrolled
from admin_panel.services.trainee.service import TraineeCourseServices

from admin_panel.models import CourseCollection
from admin_panel.services.course.dependencies import get_collection_duration


class AdminReportCourseCollectionSerializer(ModelSerializer):

  progress = serializers.SerializerMethodField()
  days_taken = serializers.SerializerMethodField()
  due_time = serializers.SerializerMethodField()
  estimated_completion_date = serializers.SerializerMethodField()
  collection_id = serializers.SerializerMethodField()

  class Meta:
    model = UserCoursesEnrolled
    fields = ['started_on', 'completed_on', 'is_completed', 'progress', 'days_taken', 
              'due_time', 'estimated_completion_date' ,'assigned_by', 'collection_id']

  def get_progress(self, obj):
    return TraineeCourseServices.get_collection_progress(obj)
  
  def get_days_taken(self, obj):
    return TraineeCourseServices.get_time_taken_to_complete(obj)
  
  def get_due_time(self, obj):
    due_days = TraineeCourseServices.get_time_taken_to_complete(obj) - obj.collection.alloted_time
    return due_days
  
  def get_estimated_completion_date(self, obj):
    return TraineeCourseServices.estimated_collection_completeion_date(obj)

  def get_collection_id(self, obj):
    return obj.collection.id

  def assigned_by(self, obj):
    return obj.collection.created_by.username

class AdminResponseCourseGroupSerializer(ModelSerializer):
    
    courses = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()

    started_on = serializers.SerializerMethodField()
    completed_on = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    days_taken = serializers.SerializerMethodField()
    due_time = serializers.SerializerMethodField()
    estimated_completion_date = serializers.SerializerMethodField()
    assigned_by = serializers.SerializerMethodField()

    def get_metadata_field(self, object_id):
      for data in self.context.get('metadata'):
        if data.get('collection_id') == object_id:
          return data
  
    class Meta:
      model = CourseCollection
      fields = [
          'id', 'title', 'description', 
          'duration', 'image', 'alloted_time', 
          'started_on', 'completed_on', 'is_completed',
          'progress', 'days_taken', 'due_time', 'estimated_completion_date',
          'assigned_by', 'courses',
      ]

    def get_started_on(self, obj):
      return self.get_metadata_field(obj.id).get('started_on')

    def get_completed_on(self, obj):
      return self.get_metadata_field(obj.id).get('completed_on')

    def get_is_completed(self, obj):
      return self.get_metadata_field(obj.id).get('is_completed')

    def get_progress(self, obj):
      return self.get_metadata_field(obj.id).get('progress')

    def get_days_taken(self, obj):
      return self.get_metadata_field(obj.id).get('days_taken')

    def get_due_time(self, obj):
      return self.get_metadata_field(obj.id).get('due_time')

    def get_estimated_completion_date(self, obj):
      return self.get_metadata_field(obj.id).get('estimated_completion_date')

    def get_assigned_by(self, obj):
      return self.get_metadata_field(obj.id).get('assigned_by')

    def get_duration(self, obj):
      return get_collection_duration(obj)

    def get_courses(self, obj):
      trainee_id = self.context.get('trainee_id')
      return [
        TraineeCourseServices.generate_course_report(course, trainee_id) 
        for course in obj.courses.all()
      ]