from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response

from admin_panel.models import CourseCollection, Course

class CourseCollectionAPIService:

  @staticmethod
  def get_collection_by_id(collection_id, user=None):
    try:
      if user:
        collection = CourseCollection.objects.get(id=collection_id, created_by=user)
      else:
        collection = CourseCollection.objects.get(id=collection_id)
      return collection
    except ObjectDoesNotExist:
      return None
    
  @staticmethod
  def get_all_collections(user=None):
    if user:
      return CourseCollection.objects.all().filter(created_by=user)
    return CourseCollection.objects.all()
  
  
  @staticmethod
  def create(request, data, user=None):
    courses = data.pop('courses')

    course_collection = CourseCollection.objects.create(**data)
    if user:
      course_collection.created_by = user
    else:
      course_collection.created_by = request.user

    for course in courses:
      try:
        course = Course.objects.get(id=course)
        course_collection.courses.add(course)
      except ObjectDoesNotExist:
        continue

    course_collection.save()
    return course_collection
  
  @staticmethod
  def get(user, collection_id):
    try:
      course = CourseCollection.objects.get(id=collection_id, created_by=user)
      return course
    except ObjectDoesNotExist:
      return None
    
  @staticmethod
  def get_all(user):
    return CourseCollection.objects.all().filter(created_by=user)
  
  @staticmethod
  def delete(request, collection_id, many=False):
    if many:
      CourseCollection.objects.filter(id__in=collection_id).delete()
    else:
      course = CourseCollectionAPIService.get(request.user, collection_id)
      course.delete()

  @staticmethod
  def update(request, course_collection, data):
    courses = []
    if 'courses' in data:
      courses = data.pop('courses')
    for key, value in data.items():
      setattr(course_collection, key, value)

    if courses:
      course_collection.courses.clear()
    for course in courses:
      try:
        course = Course.objects.get(id=course)
        course_collection.courses.add(course)
      except ObjectDoesNotExist:
        continue
    
    if data.get('removed'):
      course_collection.image = None

    course_collection.save()
    return course_collection
  

  @staticmethod
  def delete_course_from_collection(request, collection_id, course_id):
    try:
      course_collection = CourseCollectionAPIService.get(request.user, collection_id)
      course = Course.objects.get(id=course_id)
      course_collection.courses.remove(course)
      course_collection.save()
    except Exception as e:
      raise ObjectDoesNotExist
      
  
  @staticmethod
  def set_default_collection(request, collection, user=None):
    try:
      if collection.is_default:
        return Response({"message": "Collection is already default"}, status=200)
      else:
        if user:
          user.default_collection = collection
          user.save()
        else:
          request.user.default_collection = collection
          request.user.save()
        return Response({"message": "Collection set as default"}, status=200)
    except ObjectDoesNotExist:
      return Response({"message": "Collection not found"}, status=404)