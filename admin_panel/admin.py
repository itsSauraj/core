from django.contrib import admin

from django.contrib.auth.models import Permission

from admin_panel.models import User, Course, CourseModules, CourseModuleLessons, CourseCollection

# Register your models here.

admin.site.register(Permission)
admin.site.register(User)

admin.site.register(CourseCollection)
admin.site.register(Course)
admin.site.register(CourseModules)
admin.site.register(CourseModuleLessons)
