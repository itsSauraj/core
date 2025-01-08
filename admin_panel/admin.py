from django.contrib import admin

from django.contrib.auth.models import Permission

from admin_panel.models import User

# Register your models here.

admin.site.register(Permission)
admin.site.register(User)