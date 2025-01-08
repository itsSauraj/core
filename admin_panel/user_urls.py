from django.contrib import admin
from django.urls import path, include

from admin_panel.views.user.controller import UserAPIView, MentorAPIView

urlpatterns = [
  # Admin User Management API
  path('', UserAPIView.as_view(), name='admin_user_api'),

  # Mentor User Management API
  path('mentor/', MentorAPIView.as_view(), name='mentor_user_api'),
]