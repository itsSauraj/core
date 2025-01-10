from django.contrib import admin
from django.urls import path, include

from admin_panel.views.user.admin import UserAPIView
from admin_panel.views.user.member import MemberAPIView, MemberModules
from admin_panel.views.course.controller import CourseAPIView, ModuleAPIView

urlpatterns = [
  # Admin User Management APIs
  path('auth/user/', include('admin_panel.user_urls')),

  path('member/<uuid:member_id>', MemberAPIView.as_view(), name='mentor_user_api'),

  path('user/mentor/', MemberModules.get_all_mentors, name='get_all_mentors'),
  path('user/trainee/', MemberModules.get_all_trainees, name='get_all_trainees'),

  # Course Management APIs  
  path('course/', CourseAPIView.as_view(), name='course_api'),
  path('course/<uuid:course_id>', CourseAPIView.as_view(), name='course_api_with_id'),

  ## Module Management APIs
  path('course/<uuid:course_id>/module/', ModuleAPIView.as_view(), name='module_api'),
  path('course/<uuid:course_id>/module/<uuid:module_id>', ModuleAPIView.as_view(), name='module_api_with_id'),
]