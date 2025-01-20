from django.urls import path, include

from admin_panel.views.user.member import MemberAPIView, MemberModules
from admin_panel.views.course.controller import CourseAPIView, ModuleAPIView, LessonAPIView
from admin_panel.views.course.course_collection import CourseCollectionAPIView, CourseCollectionModules


urlpatterns = [
  # Admin User Management APIs
  path('auth/user/', include('admin_panel.user_urls')),

  path('member/', MemberAPIView.as_view(), name='members_api'),
  path('member/<uuid:member_id>', MemberAPIView.as_view(), name='mentor_id_apis'),

  path('user/mentor/', MemberModules.get_all_mentors, name='get_all_mentors'),
  path('user/trainee/', MemberModules.get_all_trainees, name='get_all_trainees'),

  # Course Management APIs  
  path('course/', CourseAPIView.as_view(), name='course_api'),
  path('course/<uuid:course_id>', CourseAPIView.as_view(), name='course_api_with_id'),
  #
  path('course/collection/', CourseCollectionAPIView.as_view(), name='course_collections_api'),
  path('course/collection/<uuid:collection_id>', CourseCollectionAPIView.as_view(), name='course_collection_api'),
  path('course/collection/<uuid:collection_id>/<uuid:course_id>', CourseCollectionModules.course_actions_collection, name='course_module_actions'),

  ## Module Management APIs
  path('course/<uuid:course_id>/module/', ModuleAPIView.as_view(), name='module_api'),
  path('course/<uuid:course_id>/module/<uuid:module_id>', ModuleAPIView.as_view(), name='module_api_with_id'),

  ### Lesson Management APIs
  path('course/<uuid:course_id>/module/<uuid:module_id>/lesson/', LessonAPIView.as_view(), name='lesson_api'),
  path('course/<uuid:course_id>/module/<uuid:module_id>/lesson/<uuid:lesson_id>', LessonAPIView.as_view(), name='lesson_api'),
]