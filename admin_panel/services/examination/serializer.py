import datetime

from rest_framework import serializers

from admin_panel.models import (
  Course, CourseModules, CourseModuleLessons,
  UserCourseActivity, CourseCollection, User, ScheduledExam
)

class ExamScheduleSerializer(serializers.ModelSerializer):
  class Meta:
    model = ScheduledExam
    fields = ['collection', 'exam_date', 'exam_time', 'assigned_mentor', 
              'assigned_trainee', 'created_by', 'exam_details', 'duration']
    
  def validate(self, data):
    exam_date = data['exam_date']
    current_date = datetime.datetime.now(tz=datetime.timezone.utc)
    if exam_date < current_date:
      raise serializers.ValidationError("Exam date should be greater than today's date")
    
    if exam_date == current_date:
      if datetime.datetime.today().time() > data['exam_time']:
        raise serializers.ValidationError("Exam time should be greater than current time")
    return data