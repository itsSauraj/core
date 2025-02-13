from datetime import datetime, timezone

from admin_panel.models import (
  Course, CourseModules, CourseModuleLessons,
  UserCourseActivity, CourseCollection, User, ScheduledExam
)
from admin_panel.services.notification.service import NotificationService
from admin_panel.services.mailer.factory import mailer

class ExaminationService():
  
  @staticmethod
  def create_exam(user, data):

    exam = ScheduledExam.objects.create(**data, created_by=user)

    message = f"Exam Scheduled for {exam.collection.title} on \
      {exam.exam_date} at {exam.exam_time}. Mentor assigned for this exam is \
      {exam.assigned_mentor.first_name} {exam.assigned_mentor.last_name} Kindly be prepared. for your exam."

    NotificationService.send_notification(
      sender=user,
      recipient=data.get('assigned_trainee'),
      notification_type='info',
      title='Exam Scheduled',
      message=message,
    )

    mailer.send_mail(
      'send_user_account_exam_scheduled_notification',
      user_id=data.get('assigned_trainee').id,
      exam=exam
    )
    
    return exam
  
  @staticmethod
  def get_all_exams(user):
    return ScheduledExam.objects.all().filter(created_by=user).order_by('-created_at')
  
  @staticmethod
  def get_exam_by_id(user, exam_id):
    return ScheduledExam.objects.get(created_by=user, id=exam_id)
  
  @staticmethod
  def delete_exam(user, exam_id):
    exam = ScheduledExam.objects.get(created_by=user, id=exam_id)
    exam.delete()
    return True
  
  @staticmethod
  def update_exam(user, exam_id, data, notify):
    exam = ScheduledExam.objects.get(created_by=user, id=exam_id)
    for key, value in data.items():
      setattr(exam, key, value)
    exam.updated_at = datetime.now(tz=timezone.utc)
    exam.save()

    if notify:
      message = f"Exam Scheduled for {exam.collection.title} on \
        {exam.exam_date} at {exam.exam_time}. Mentor assigned for this exam is \
        {exam.assigned_mentor.first_name} {exam.assigned_mentor.last_name} Kindly be prepared. for your exam."

      NotificationService.send_notification(
        sender=user,
        recipient=exam.assigned_trainee,
        notification_type='info',
        title='Exam ReScheduled',
        message=message,
      )

      mailer.send_mail(
        'send_user_account_exam_scheduled_notification',
        user_id=exam.assigned_trainee.id,
        exam=exam,
        rescheduled=True
      )

    return exam