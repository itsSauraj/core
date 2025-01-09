from django.contrib import admin
from django.urls import path, include

from admin_panel.views.user.admin import UserAPIView
from admin_panel.views.user.member import MemberAPIView, MemberModules

urlpatterns = [
  # Admin User Management APIs
  path('auth/user/', include('admin_panel.user_urls')),

  path('member/<uuid:member_id>', MemberAPIView.as_view(), name='mentor_user_api'),

  path('user/mentor/', MemberModules.get_all_mentors, name='get_all_mentors'),
  path('user/trainee/', MemberModules.get_all_trainees, name='get_all_trainees'),
]