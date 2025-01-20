from admin_panel.models import Course, CourseCollection, UserCoursesEnrolled

# from admin_panel.services.user.service import UserAPIService


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