import calendar
from datetime import timedelta

from datetime import datetime, timezone

from admin_panel.models import CourseCollection, UserCoursesEnrolled, UserCourseActivity,\
  UserCourseProgress, CourseModuleLessons
from admin_panel.services.course.dependencies import get_course_duration
from admin_panel.services.course.serializer import ResponseReportModuleSerializer
from admin_panel.services.user.service import UserAPIService
from admin_panel.services.notification.service import NotificationService
from admin_panel.services.mailer.factory import mailer


class TraineeCourseServices:

  @staticmethod
  def get_enrollect_collection(collection_id, assigned_by=None):
    try:
      collection = UserCoursesEnrolled.objects.get(collection_id=collection_id, assigned_by=assigned_by)
      return collection
    except Exception as e:
      return None
  
  @staticmethod
  def create(assignee, data):
    user = data['user']
    collections = CourseCollection.objects.filter(id__in=data['collection'])

    try:
      prev_collections = user.enrolled_courses.values_list('collection_id', flat=True)
    except Exception as e:
      prev_collections = UserAPIService.get_user_by_id(user).enrolled_courses.values_list('collection_id', flat=True)
    
    new_collections = [
      collection for collection in collections 
      if collection.id not in prev_collections
    ]

    for collection in new_collections:
      enrollment = UserCoursesEnrolled.objects.create(
        user=user,
        collection=collection,
        assigned_by=assignee
      )
      user.enrolled_courses.add(enrollment)

  @staticmethod
  def delete(request, data):
    user_id = data['user']
    collection_ids = data['collection']

    for collection_id in collection_ids:
      collection = UserCoursesEnrolled.objects.filter(user_id=user_id, collection_id=collection_id, 
                                                      assigned_by=request.user)
      if collection.exists():
        collection.delete()
      else:
        return False
    return True
  

  @staticmethod
  def start_user_course(request, collection_id, data):
    
    EnrolledCollection = request.user.enrolled_courses.filter(collection_id=collection_id)
    if not EnrolledCollection.exists():
      return None
  
    if not EnrolledCollection.first().started_on:
      EnrolledCollection.update(
        started_on=datetime.now(timezone.utc)
      )
      NotificationService.send_notification(
        sender=request.user,
        recipient=request.user.created_by,
        title="Course Started",
        message="{} {} has started the course {}"
          .format(request.user.first_name, request.user.last_name, 
                  EnrolledCollection.first().collection.title),
        notification_type='success'
      )

    user_course_activity, created = UserCourseActivity.objects.get_or_create(**data)
    return user_course_activity

  
  @staticmethod
  def mark_lesson_as_completed(request, collection_id, data):
    user_course_progress, created = UserCourseProgress.objects.get_or_create(**data)

    get_course_progress = TraineeCourseServices.get_course_progress(request.user.id, user_course_progress.course.id)

    if get_course_progress == 100:
      UserCourseActivity.objects.filter(user=user_course_progress.user, course=user_course_progress.course).update(
        completed_on=datetime.now(timezone.utc)
      )

      NotificationService.send_notification(
        sender=request.user,
        recipient=request.user.created_by,
        title="Course Completed",
        message="{} {} has completed the course {} as current collection progress is {}"
          .format(request.user.first_name, request.user.last_name, 
                  user_course_progress.course.title, get_course_progress),
        notification_type='success'
      )

      current_course_collection = UserCoursesEnrolled.objects.filter(user=request.user.id, collection_id=collection_id)

      if TraineeCourseServices.get_collection_progress(current_course_collection.first()) == 100:
        current_course_collection.update(
          completed_on=datetime.now(timezone.utc),
          is_completed=True
        )
        NotificationService.send_notification(
          sender=request.user,
          recipient=request.user.created_by,
          title="Collection Completed",
          message="{} {} has completed the collection {}"
            .format(request.user.first_name, request.user.last_name, 
                    current_course_collection.first().collection.title),
          notification_type='success'
        )

        mailer.send_mail(
          'send_user_collection_completed_notification',
          user_id=request.user.id,
          collection=current_course_collection.first().collection
        )

    return user_course_progress
  
  @staticmethod
  def unmark_lesson_as_completed(request, collection_id, data):
    user_course_progress = UserCourseProgress.objects.filter(**data)

    if user_course_progress.exists():
      get_course_progress = TraineeCourseServices.get_course_progress(request.user.id, user_course_progress.first().course.id)

      if get_course_progress == 100:
        UserCourseActivity.objects.filter(user=user_course_progress.first().user, course=user_course_progress.first().course).update(
          completed_on=None
        )

        current_course_collection = UserCoursesEnrolled.objects.filter(user=request.user.id, collection_id=collection_id)

        if TraineeCourseServices.get_collection_progress(current_course_collection.first()) == 100:
          current_course_collection.update(
            completed_on=None,
            is_completed=False
          )

      user_course_progress.delete()

    else:
      return False
    return True
  
  @staticmethod
  def get_completed_lessons(user_id, course_id):
    completed_lessons = UserCourseProgress.objects.filter(user_id=user_id, course_id=course_id)
    return completed_lessons
  
  @staticmethod
  def get_course_progress(user_id, course_id):
    lessons_completed = UserCourseProgress.objects.filter(user_id=user_id, course_id=course_id)
    total_lessons = CourseModuleLessons.objects.filter(module__course_id=course_id).count()
    progress_in_percent = (lessons_completed.count() / total_lessons) * 100
    return round(progress_in_percent, 2)
    
  @staticmethod
  def get_collection_progress(current_collection):
    collection_courses = current_collection.collection.courses.all()
    progress = 0
    for course in collection_courses:
      progress += TraineeCourseServices.get_course_progress(current_collection.user.id, course.id)
    course_count = collection_courses.count()
    if course_count == 0:
        return 0
    return round(progress / course_count, 2)
    
  @staticmethod
  def estimated_collection_completeion_date(current_collection):
    if not current_collection.started_on:
      return None

    current_date = current_collection.started_on
    alloted_number_of_days = current_collection.collection.alloted_time

    while alloted_number_of_days > 0:
        current_date += timedelta(days=1)
        if calendar.weekday(current_date.year, current_date.month, current_date.day) != calendar.SUNDAY:
            alloted_number_of_days -= 1

    return current_date

  @staticmethod
  def get_time_taken_to_complete(current_collection):
    start_date = current_collection.started_on
    todays_date = datetime.now(timezone.utc)
    completed_on = current_collection.completed_on
    estimate_date = TraineeCourseServices.estimated_collection_completeion_date(current_collection)

    if not start_date or not estimate_date:
      return 0
    
    if completed_on:
      days_taken = (completed_on - start_date).days
    else:   
      days_taken = (todays_date - start_date).days

    return days_taken
  
  @staticmethod
  def generate_course_report(course, user_id):
    modules = ResponseReportModuleSerializer(course.modules, context={'user_id': user_id}, many=True).data
    user_activity_obj = UserCourseActivity.objects.filter(user_id=user_id, course_id=course.id).first()

    if user_activity_obj is None:
      is_started = False
      started_on = None
      is_completed = False
      completed_on = None
    else:
      is_started = user_activity_obj.is_started()
      started_on = user_activity_obj.started_on
      is_completed = user_activity_obj.is_completed()
      completed_on = user_activity_obj.completed_on

    return {
      'id': course.id, 
      'title': course.title,
      'description': course.description,
      'duration': get_course_duration(course),
      'progress': TraineeCourseServices.get_course_progress(user_id, course.id),
      'is_started': is_started,
      'started_on': started_on,
      'is_completed': is_completed,
      'completed_on': completed_on,
      'modules': modules
    }