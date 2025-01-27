from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from admin_panel.roles_and_permissions.roles import IsInGroup
from admin_panel.roles_and_permissions.decorators import group_required

from admin_panel.services.trainee.serializer import CreateUserCollectionSerializer, ReportCourseCollectionSerializer, \
  CreateUserCourseActivitySerializer, CreateLessonProgressSerializer, ResponeUserCourseProgressSerializer, \
    LessonLearnedSerializer, DeleteUserCollectionSerializer, ResponseTraineeAssignedCollectionsMinifiedSerializer
from admin_panel.services.trainee.service import TraineeCourseServices
from admin_panel.services.course.service import CourseAPIService
from admin_panel.services.user.service import UserAPIService
from admin_panel.services.course.serializer import ResponseCollectionsMinifiedSerializer

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
  

  def delete(self, request):

    serializer = DeleteUserCollectionSerializer(data=request.data)

    if not serializer.is_valid():
      return Response(serializer.errors, status=400)
    
    status = TraineeCourseServices.delete(request, serializer.validated_data)
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

  @staticmethod
  @api_view(['GET'])
  @group_required(['Admin'])
  def get_minified_user_collections(request, trainee_id):

    if trainee_id is None:
      return Response({"message": "Trainee ID is required"}, status=400)
    
    try:
        trainee = UserAPIService.get_trainee(trainee_id, request.user)
        assigned_collections = trainee.enrolled_courses.all()
    except AttributeError:
        return Response({"message": "Trainee not found or has no enrolled courses"}, status=404)
    
    all_collections = CourseAPIService.get_all_collections(request.user)
    un_assigned_collections = []
    for collection in all_collections:
        is_assigned = False
        for assigned in assigned_collections:
            if assigned.collection.id == collection.id:
                is_assigned = True
                break
        if not is_assigned:
            un_assigned_collections.append(collection)


    context = {
      "assigned_collections": ResponseTraineeAssignedCollectionsMinifiedSerializer(assigned_collections, many=True).data,
      "available_collections": ResponseCollectionsMinifiedSerializer(un_assigned_collections, many=True).data
    }

    return Response(context, status=200)