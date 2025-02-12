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