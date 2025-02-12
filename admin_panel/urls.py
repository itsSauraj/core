from django.urls import path, include

from admin_panel.views.user.member import MemberAPIView, MemberModules
from admin_panel.views.user.profile import ProfileAPIViewSet
from admin_panel.views.course.controller import CourseAPIView, ModuleAPIView, LessonAPIView
from admin_panel.views.course.course_collection import CourseCollectionAPIView, CourseCollectionModules
from admin_panel.views.trainee.controller import TraineeCourseAPIView, TraineeAPIView
from admin_panel.views.examination.controller import ExaminationAPIView

from rest_framework.routers import DefaultRouter
from admin_panel.views.notifications import NotificationViewSet
from admin_panel.views.dashboard import DashboardViewSet

router = DefaultRouter()

# Registering ViewSets Notifications
router.register(r'notifications', NotificationViewSet, basename='notification')

# Registering ViewSets Dashboard
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

# Registering ViewSets Profile
router.register(r'profile', ProfileAPIViewSet, basename='profile')

urlpatterns = [
  # Router ViewSet APIs
  path('', include(router.urls)),

  # Admin User Management APIs
  path('auth/user/', include('admin_panel.user_urls')),

  # Member Management APIs
  path('member/<uuid:member_id>', MemberAPIView.as_view(), name='mentor_id_apis'),
  path('member/', MemberAPIView.as_view(), name='members_api'),
  path('user/mentor/', MemberModules.get_all_mentors, name='get_all_mentors'),
  path('user/trainee/', MemberModules.get_all_trainees, name='get_all_trainees'),
  path('user/trainee/<uuid:trainee_id>/report', MemberModules.generate_report, name='generate_report'),

  # Course Management APIs  
  path('course/', CourseAPIView.as_view(), name='course_api'),
  path('course/<uuid:course_id>', CourseAPIView.as_view(), name='course_api_with_id'),

  # Course Collection Management APIs
  path('course/collection/', CourseCollectionAPIView.as_view(), name='course_collections_api'),
  path('course/collection/<uuid:collection_id>', CourseCollectionAPIView.as_view(), name='course_collection_api'),
  path('course/collection/<uuid:collection_id>/default', CourseCollectionModules.set_default_collection, name='set_default_collection'),
  path('course/collection/<uuid:collection_id>/<uuid:course_id>', CourseCollectionModules.course_actions_collection, name='course_module_actions'),

  ## Module Management APIs
  path('course/<uuid:course_id>/module/', ModuleAPIView.as_view(), name='module_api'),
  path('course/<uuid:course_id>/module/<uuid:module_id>', ModuleAPIView.as_view(), name='module_api_with_id'),

  ### Lesson Management APIs
  path('course/<uuid:course_id>/module/<uuid:module_id>/lesson/', LessonAPIView.as_view(), name='lesson_api'),
  path('course/<uuid:course_id>/module/<uuid:module_id>/lesson/<uuid:lesson_id>', LessonAPIView.as_view(), name='lesson_api'),

  ### Trainee Course Management APIs
  path('trainee/course/', TraineeCourseAPIView.as_view(), name='trainee_course_collection_api'),

  ### For trainee to view course
  path('member/collection/', TraineeAPIView.get_all_assigned_collections, name='trainee_assigned_collections'),
  path('trainee/collection/mini/<uuid:trainee_id>', TraineeAPIView.get_minified_user_collections, name='trainee_assigned_collections_mini'),
  path('member/<uuid:collection_id>/<uuid:course_id>', TraineeAPIView.user_course_actions, name='trainee_course_action'),
  path('member/action/lesson', TraineeAPIView.user_course_lessson_actions, name='trainee_course_lesson_action'),

  # Examination Management APIs
  path('exam/', ExaminationAPIView.as_view(), name='exam_apis'),
  path('exam/<uuid:exam_id>/', ExaminationAPIView.as_view(), name='exam_api_with_id'),
]

