import uuid
from datetime import timedelta, datetime, timezone

from django.db import models
from django.contrib.auth.models import AbstractUser, Group

# Create your models here.
class BaseModel(models.Model):
  created_at = models.DateTimeField(('created at'), auto_now_add=True, null=False, blank=False)
  updated_at = models.DateTimeField(('updated at'), auto_now=True)
  deleted_at = models.DateTimeField(('deleted at'), null=True, blank=True, on_delete=models.SET(datetime.now(timezone.utc)))

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  
  class Meta:
    abstract = True


class User(BaseModel, AbstractUser):

  phone_number = models.CharField(('phone number'),max_length=15, null=True, blank=True)
  birth_date = models.DateField(('birth date'), null=True, blank=True)
  address = models.TextField(('address'), null=True, blank=True)
  
  email = models.EmailField(("email address"), unique=True)

  created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='creator')

  def __str__(self):
    return self.username
  
  def save(self, *args, **kwargs):
    if not self.pk:  # Check if the user is being created
      self.set_password(self.password)  # Hash the password
    super(User, self).save(*args, **kwargs)

  # Get all permissions of the user
  def get_permissions(self):
    return self.get_all_permissions()
  
  # Get all mentors of the user
  def get_created_mentors(self):
    return User.objects.filter(created_by=self, groups__name='Mentor')
  
  # Get all trainees of the user
  def get_created_trainees(self):
    return User.objects.filter(created_by=self, groups__name='Trainee')
  
  # Get all courses of the user
  def get_created_courses(self):
    return self.course_set.all()

class Course(BaseModel):
  title = models.CharField(('course title'), max_length=255, null=False, blank=False)
  description = models.TextField(('course description'), null=True, blank=True)
  created_by = models.ForeignKey(User, related_name='course')

  def __str__(self):
    return self.title
  
  def save(self, *args, **kwargs):
    if not self.sequence:
      self.sequence = Course.objects.filter(created_by=self.created_by).count() + 1
    super(Course, self).save(*args, **kwargs)
  
  # Get all modules of the course
  def get_all_modules(self):
    return self.modules.filter(parnet_module__isnull=True).order_by('sequence')
  
  # Get all lessons of the course
  def get_complete_structure(self):
    modules = self.get_all_modules()
    complete_structure = []
    for module in modules:
      module_structure = {
        'module': module,
        'sub_modules': module.get_sub_modules()
      }
      complete_structure.append(module_structure)
    return complete_structure
  
class CourseModules(BaseModel):
  title = models.CharField(('module title'), max_length=255, null=False, blank=False)
  description = models.TextField(('module description'), null=True, blank=True)
  course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
  parnet_module = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_modules', verbose_name='parent module')
  sequence = models.IntegerField(('module sequence'), default=0)

  def __str__(self):
    return self.title
  
  def save(self, *args, **kwargs):
    if not self.sequence:
      self.sequence = CourseModules.objects.filter(course=self.course, parnet_module=self.parnet_module).count() + 1
    super(CourseModules, self).save(*args, **kwargs)
  
  def get_sub_modules(self):
    return CourseModules.objects.filter(parnet_module=self).order_by('sequence')

  def get_all_lessons(self):
    return self.lessons.all().order_by('sequence')
  
class CourseModuleLessons(BaseModel):
  title = models.CharField(('lesson title'), max_length=255, null=False, blank=False)
  description = models.TextField(('lesson description'), null=True, blank=True)
  course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
  module = models.ForeignKey(CourseModules, on_delete=models.CASCADE, related_name='lessons')
  sequence = models.IntegerField(('lesson sequence'), default=0)
  duration = models.DurationField(('lesson duration'), default=timedelta(hours=0, minutes=0, seconds=0)) # Duration in hours (e.g. 1:30:00)

  def __str__(self):
    return self.title
  
  def save(self, *args, **kargs):
    if not self.sequence:
      self.sequence = CourseModuleLessons.objects.filter(course=self.course, module=self.module).count() + 1
    super(CourseModuleLessons, self).save(*args, **kargs)
