from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework.permissions import IsAuthenticated

from admin_panel.services.mailer.emails import register_all

urlpatterns = [
  path('admin/', admin.site.urls),
  path('api/', include('admin_panel.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

def register_functions():
  register_all()

register_functions()