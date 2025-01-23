from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from admin_panel.models import CourseCollection, UserCoursesEnrolled
from admin_panel.services.trainee.service import TraineeCourseServices

from admin_panel.models import CourseCollection
from admin_panel.services.course.dependencies import get_course_duration, get_collection_duration


class AdminReportCourseCollectionSerializer(ModelSerializer):

  progress = serializers.SerializerMethodField()
  days_taken = serializers.SerializerMethodField()
  due_time = serializers.SerializerMethodField()
  estimated_completion_date = serializers.SerializerMethodField()

  class Meta:
    model = UserCoursesEnrolled
    fields = ['started_on', 'completed_on', 'is_completed', 'progress', 'days_taken', 
              'due_time', 'estimated_completion_date' ,'assigned_by']

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

class AdminResponseCourseGroupSerializer(ModelSerializer):
    courses = serializers.SerializerMethodField()
    duration = serializers.SerializerMethodField()
    extra_fields = serializers.SerializerMethodField()

    class Meta:
        model = CourseCollection
        fields = [
            'id', 'title', 'description', 
            'duration', 'image', 'alloted_time', 
            'courses', 'extra_fields'
        ]

    def get_duration(self, obj):
        return get_collection_duration(obj)

    def get_courses(self, obj):
        trainee_id = self.context.get('trainee_id')
        return [
            TraineeCourseServices.generate_course_report(course, trainee_id) 
            for course in obj.courses.all()
        ]
  
    def get_extra_fields(self, obj):
        return {
            key: value for key, value in self.context.items() 
            if key not in ['trainee_id', 'view', 'request', 'user']
        }