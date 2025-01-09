from django.contrib import admin
from django.urls import path, include

from rest_framework.permissions import IsAuthenticated

urlpatterns = [
  path('admin/', admin.site.urls),
  path('api/admin/', include('admin_panel.urls')),
  path('api/auth/user/', include('admin_panel.user_urls')),
]