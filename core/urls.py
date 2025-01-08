from django.contrib import admin
from django.urls import path, include

from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
  path('admin/', admin.site.urls),
  path('api/admin/', include('admin_panel.urls')),
  path('api/auth/user/', include('admin_panel.user_urls')),

  # Auth Token APIs
  path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
  path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]