from django.contrib import admin
from django.urls import path, include

from admin_panel.views.user.admin import UserAPIView
from admin_panel.views.user.member import MemberAPIView

from admin_panel.views.auth.controller import CustomTokenObtainSlidingView, CustomTokenRefreshSlidingView, \
                                          LogoutView

urlpatterns = [
  # Admin User Management API
  path('', UserAPIView.as_view(), name='admin_user_api'),
  path('<uuid:id>/', UserAPIView.as_view(), name='admin_user_api'),

  # Membor and Trainee User Management API
  path('member/', MemberAPIView.as_view(), name='mentor_user_api'),

  # Auth Token APIs
  path('login/', CustomTokenObtainSlidingView.as_view(), name='user_login'),
  path('refresh/', CustomTokenRefreshSlidingView.as_view(), name='user_refresh'),
  path('logout/', LogoutView.as_view(), name='user_logout'),
]