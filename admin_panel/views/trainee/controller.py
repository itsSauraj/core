from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from admin_panel.roles_and_permissions.roles import IsInGroup
from admin_panel.roles_and_permissions.decorators import group_required

from admin_panel.services.trainee.serializer import CreateUserCollectionSerializer, ReportCourseCollectionSerializer, \
  CreateUserCourseActivitySerializer, CreateLessonProgressSerializer, ResponeUserCourseProgressSerializer, LessonLearnedSerializer
from admin_panel.services.trainee.service import TraineeCourseServices
from admin_panel.services.course.service import CourseAPIService

class TraineeCourseAPIView(APIView):
  def get_permissions(self):
    return [IsAuthenticated(), IsInGroup('Admin')]
    
  def post(self, request):
    
    serializer = CreateUserCollectionSerializer(data=request.data)

    if not serializer.is_valid():
      return Response(serializer.errors, status=400)
    
    for collection in serializer.validated_data['collection']:
      if collection.created_by != request.user:
        return Response({"message": "You can not assign collection of which you are not the owner"}, status=400)
    
    TraineeCourseServices.create(request, serializer.validated_data)
    
    return Response({"message": "Added to collection"}, status=201)
  

  def delete(self, request, collection_id=None):
    if collection_id is None:
      return Response({"message": "Collection ID is required"}, status=400)
    
    status = TraineeCourseServices.delete(request, collection_id)
    if not status:
      return Response({"message": "Collection not found"}, status=404)
    
    return Response(status=204)
  

class TraineeAPIView():

  @staticmethod
  @api_view(['GET'])
  @group_required(['Trainee', 'Admin'])
  def get_all_assigned_collections(request):

    assigned_collections = request.user.enrolled_courses.all()
    if assigned_collections.count() == 0:
      return Response({"message": "No assigned collections"}, status=404)
    
    started_courses_by_collection = {
      str(metadata.collection.id): {
        str(course.id): TraineeCourseServices.get_course_progress(request.user.id, course.id) 
        for course in metadata.collection.courses.all() 
          if CourseAPIService.course_is_started(course.id, request.user.id)
      }
      for metadata in assigned_collections
    }

    context = {
      "collections": ReportCourseCollectionSerializer(assigned_collections, many=True).data,
      "started_courses": started_courses_by_collection
    }
    
    return Response(context, status=200)
  

  @staticmethod
  @api_view(['GET', 'POST'])
  @group_required(['Trainee', 'Admin'])
  def user_course_actions(request, collection_id, course_id):
    if course_id is None:
      return Response({"message": "Course ID is required"}, status=400)

    if request.method == 'GET':
      return TraineeAPIView.get_assigned_course(request, course_id)
    elif request.method == 'POST':
      return TraineeAPIView.start_course(request, collection_id, course_id)
    else:
      return Response({"message": "Method not allowed"}, status=405)

  @staticmethod
  def get_assigned_course(request, course_id):
    try:
      assigned_courses = request.user.get_enrolled_courses_list()
      if assigned_courses is None:
        return Response({"message": "Course not found"}, status=404)
      
      assigned_by = assigned_courses[0].created_by

      assigned_course = next((course for course in assigned_courses if course.id == course_id), None)
      if assigned_course:
        course_structure = CourseAPIService.get_course_structure(assigned_course.id, assigned_by)
        course_completed_lessons = TraineeCourseServices.get_completed_lessons(request.user.id, course_id)
        completed_lessons_list = [progress_item['lesson'] for progress_item in 
            ResponeUserCourseProgressSerializer(course_completed_lessons, many=True).data]
        context = {
          "course": course_structure,
          "isStarted": CourseAPIService.course_is_started(course_id, request.user.id).exists(),
          "completed_lessons": completed_lessons_list,
        }
        return Response(context, status=200)
      else: 
        return Response({"message": "Course not found"}, status=404)
    except Exception as e:
      return Response({"message": "Internal Server Error"}, status=500)

  @staticmethod
  def start_course(request, collection_id, course_id):
    if course_id is None:
      return Response({"message": "Course ID is required"}, status=400)
    
    started_request = {
      "course": course_id,
      "user": request.user.id
    }

    serializer = CreateUserCourseActivitySerializer(data=started_request)

    if not serializer.is_valid():
      return Response(serializer.errors, status=400)
    
    start_user_course = TraineeCourseServices.start_user_course(request, collection_id, serializer.validated_data)
    if start_user_course is None:
      return Response({"message": "Course not found"}, status=404)
    
    return Response(True, status=200)


  @staticmethod
  @api_view(['POST'])
  @group_required(['Trainee', 'Admin'])
  def user_course_lessson_actions(request):

    serializer = LessonLearnedSerializer(data=request.data)

    if not serializer.is_valid():
      return Response(serializer.errors, status=400)
    
    validated_data = serializer.validated_data

    if request.method == 'POST':
      return TraineeAPIView.mark_lesson_as_completed(request, validated_data['collection_id'],
                                        validated_data['course_id'], validated_data['lesson_id']) 
    else:
      return Response({"message": "Method not allowed"}, status=405)
    
  @staticmethod
  def mark_lesson_as_completed(request, collection_id, course_id, lesson_id):

    requested_data = {
      "course": course_id,
      "lesson": lesson_id,
      "user": request.user.id,
    }

    serializer = CreateLessonProgressSerializer(data=requested_data)

    if not serializer.is_valid():
      return Response(serializer.errors, status=400)
    
    try:
      user_course_progress = TraineeCourseServices.mark_lesson_as_completed(request, collection_id, serializer.validated_data)
      if user_course_progress is None:
        return Response({"message": "Lesson not found"}, status=404)
    except Exception as e:
      return Response(False, status=404)
    return Response(True, status=200)
