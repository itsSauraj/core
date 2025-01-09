from django.contrib import admin
from django.urls import path, include

from rest_framework.permissions import IsAuthenticated

from admin_panel.views.auth.controller import CustomTokenObtainSlidingView

urlpatterns = [
  path('admin/', admin.site.urls),
  path('api/admin/', include('admin_panel.urls')),
  path('api/auth/user/', include('admin_panel.user_urls')),

  # Auth Token APIs
  path('api/auth/login/', CustomTokenObtainSlidingView.as_view(), name='user_login'),
]