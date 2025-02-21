import datetime

from rest_framework import serializers

from admin_panel.models import ScheduledExam

class ExamScheduleSerializer(serializers.ModelSerializer):
  class Meta:
    model = ScheduledExam
    fields = ['collection', 'exam_date', 'exam_time', 'assigned_mentor', 
              'assigned_trainee', 'created_by', 'exam_details', 'duration']
    
  def validate(self, data):
    exam_date = data['exam_date']
    current_date = datetime.datetime.now(tz=datetime.timezone.utc)
    if exam_date < current_date:
      raise serializers.ValidationError("Exam date should be same or greater than today's date")
    
    if exam_date == current_date:
      if datetime.datetime.today().time() > data['exam_time']:
        raise serializers.ValidationError("Exam time should be greater than current time")
    return data
  
class ResponseExamScheduleSerializer(serializers.ModelSerializer):
  assigned_mentor = serializers.SerializerMethodField()
  assigned_trainee = serializers.SerializerMethodField()
  collection = serializers.SerializerMethodField()
  created_by = serializers.SerializerMethodField()
  exam_details = serializers.SerializerMethodField()

  class Meta:
    model = ScheduledExam
    fields = ['id', 'collection', 'exam_date', 'exam_time', 'assigned_mentor', 
              'assigned_trainee', 'created_by', 'exam_details', 'duration']
    
  def get_assigned_mentor(self, obj):
    return {
      'id': obj.assigned_mentor.id,
      'first_name': obj.assigned_mentor.first_name,
      'last_name': obj.assigned_mentor.last_name,
      'email': obj.assigned_mentor.email,
      'avatar': obj.assigned_mentor.avatar.url if obj.assigned_mentor.avatar else None,
    }
  
  def get_assigned_trainee(self, obj):
    return {
      'id': obj.assigned_trainee.id,
      'first_name': obj.assigned_trainee.first_name,
      'last_name': obj.assigned_trainee.last_name,
      'email': obj.assigned_trainee.email,
      'avatar': obj.assigned_trainee.avatar.url if obj.assigned_trainee.avatar else None,
    }
  
  def get_collection(self, obj):
    courses = [
        {
          'id': course.id,
          'title': course.title,
        }
      for course in obj.collection.courses.all()
    ]
    return {
      'id': obj.collection.id,
      'title': obj.collection.title,
      'courses': courses,
    }
  
  def get_created_by(self, obj):
    return {
      'id': obj.created_by.id,
      'first_name': obj.created_by.first_name,
      'last_name': obj.created_by.last_name,
      'email': obj.created_by.email,
    }
  
  def get_exam_details(self, obj):
    if self.context.get('trainee'):
      current_date = datetime.datetime.now(tz=datetime.timezone.utc)
      current_time  = datetime.datetime.today().time()
      if obj.exam_date > current_date:
        if obj.exam_time > current_time:
          return ""
      return obj.exam_details
    return obj.exam_details