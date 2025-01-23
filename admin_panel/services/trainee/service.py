from datetime import datetime, timezone

from admin_panel.models import CourseCollection, UserCoursesEnrolled, UserCourseActivity,\
  UserCourseProgress, CourseModuleLessons

class TraineeCourseServices:

  @staticmethod
  def get_enrollect_collection(collection_id, assigned_by=None):
    try:
      collection = UserCoursesEnrolled.objects.get(collection_id=collection_id, assigned_by=assigned_by)
      return collection
    except Exception as e:
      return None
  
  @staticmethod
  def create(request, data):
    user = data['user']
    collections = CourseCollection.objects.filter(id__in=data['collection'])
    
    # Get previously enrolled collections
    prev_collections = user.enrolled_courses.values_list('collection_id', flat=True)
    
    # Filter out already enrolled collections
    new_collections = [
      collection for collection in collections 
      if collection.id not in prev_collections
    ]
    
    # Create enrollments for new collections
    for collection in new_collections:
      enrollment = UserCoursesEnrolled.objects.create(
        user=user,
        collection=collection,
        assigned_by=request.user
      )
      user.enrolled_courses.add(enrollment)

  @staticmethod
  def delete(request, collection_id):
    collection = TraineeCourseServices.get_enrollect_collection(collection_id, request.user)
    if collection:
      collection.delete()
      return True
    return False
  

  @staticmethod
  def start_user_course(request, collection_id, data):
    
    EnrolledCollection = request.user.enrolled_courses.filter(collection_id=collection_id)
    if not EnrolledCollection.exists():
      return None
  
    if not EnrolledCollection.first().started_on:
      EnrolledCollection.update(
        started_on=datetime.now(timezone.utc)
      )

    user_course_activity, created = UserCourseActivity.objects.get_or_create(**data)
    return user_course_activity

  
  @staticmethod
  def mark_lesson_as_completed(request, collection_id, data):
    user_course_progress, created = UserCourseProgress.objects.get_or_create(**data)

    course_activity = UserCourseActivity.objects.get(user=user_course_progress.user, 
                                                    course=user_course_progress.course)
    get_course_progress = TraineeCourseServices.get_course_progress(request.user.id, user_course_progress.course.id)
    if get_course_progress == 100:
      course_activity.completed_on = datetime.now(timezone.utc)
      if TraineeCourseServices.get_collection_progress(request.user.id, collection_id) == 100:
        UserCoursesEnrolled.objects.filter(user=request.user, collection_id=collection_id).update(
          completed_on=datetime.now(timezone.utc),
          is_completed=True
        )
      
    return user_course_progress
  
  @staticmethod
  def get_completed_lessons(user_id, course_id):
    completed_lessons = UserCourseProgress.objects.filter(user_id=user_id, course_id=course_id)
    return completed_lessons
  
  @staticmethod
  def get_course_progress(user_id, course_id):
    lessons_completed = UserCourseProgress.objects.filter(user_id=user_id, course_id=course_id)
    total_lessons = CourseModuleLessons.objects.filter(module__course_id=course_id).count()
    progress_in_percent = (lessons_completed.count() / total_lessons) * 100
    return progress_in_percent
    

  @staticmethod
  def get_collection_progress(user_id, collection_id):
    current_collection = UserCoursesEnrolled.objects.filter(user_id=user_id, collection_id=collection_id).first()
    collection_courses = current_collection.collection.courses.all()
    progress = 0
    for course in collection_courses:
      progress += TraineeCourseServices.get_course_progress(user_id, course.id)
    return progress / collection_courses.count()
    