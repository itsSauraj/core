import uuid
from datetime import timedelta, datetime, timezone

from django.db import models
from django.contrib.auth.models import AbstractUser, Group

from django.db.models.signals import pre_delete, post_delete

from admin_panel.manager import CustomUserManager

from django_softdelete.models import SoftDeleteModel
from django.contrib.contenttypes.fields import GenericRelation
from django.db import transaction

# Create your models here.
class TimeStampedModel(models.Model):
  created_at = models.DateTimeField(('created at'), auto_now_add=True, null=False, blank=False)
  updated_at = models.DateTimeField(('updated at'), auto_now=True)

  class Meta:
    abstract = True

class BaseModel(TimeStampedModel, SoftDeleteModel):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

  class Meta:
    abstract = True
    

class User(BaseModel, AbstractUser):

  # TODO: Add employee ID field

  phone_number = models.CharField(('phone number'),max_length=15, null=True, blank=True)
  birth_date = models.DateField(('birth date'), null=True, blank=True)
  address = models.TextField(('address'), null=True, blank=True)
  employee_id = models.CharField(('employee id'), max_length=255, null=True, blank=True, unique=True)
  joining_date = models.DateField(('joining date'), null=True, blank=True)

  email = models.EmailField(("email address"), unique=True)

  created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='creator')

  objects = CustomUserManager()

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
  created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='course')

  def __str__(self):
    return self.title
  
  # Get all modules of the course
  def get_all_modules(self):
    return self.modules.filter(parent_module__isnull=True).order_by('sequence')
  
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
  title = models.CharField(('module title'), max_length=255, null=False, blank=False, unique=False)
  description = models.TextField(('module description'), null=True, blank=True)
  course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True, related_name='modules')
  parent_module = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_modules', verbose_name='parent module')
  sequence = models.IntegerField(('module sequence'), default=0)

  def __str__(self):
    try:
      return f"{self.sequence} {self.title} - {self.course.title}"
    except:
      return f"{self.sequence} {self.title}"
  
  def save(self, *args, **kwargs):
    if not self.sequence:
      if self.parent_module:
        self.sequence = CourseModules.objects.filter(parent_module=self.parent_module).count() + 1
      else:
        self.sequence = CourseModules.objects.filter(course=self.course).count() + 1
    super(CourseModules, self).save(*args, **kwargs)
  
  @property
  def get_sub_modules(self):
    return CourseModules.objects.filter(parent_module=self).order_by('sequence')

  @property
  def get_all_lessons(self):
    return self.lessons.all().order_by('sequence')
  
class CourseModuleLessons(BaseModel):
  title = models.CharField(('lesson title'), max_length=255, null=False, blank=False)
  description = models.TextField(('lesson description'), null=True, blank=True)
  course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True, related_name='lessons')
  module = models.ForeignKey(CourseModules, on_delete=models.CASCADE, null=True, blank=True, related_name='lessons')
  sequence = models.IntegerField(('lesson sequence'), default=0)
  duration = models.DurationField(('lesson duration'), default=timedelta(hours=0, minutes=0, seconds=0)) # Duration in hours (e.g. 1:30:00)

  def __str__(self):
    try:
      return f"{self.sequence} {self.title} - {self.module.title} - {self.course.title}"
    except:
      return f"{self.sequence} {self.title}"
  
  
  def save(self, *args, **kwargs):
    if not self.sequence:
      self.sequence = CourseModuleLessons.objects.filter(module=self.module).count() + 1
    super(CourseModuleLessons, self).save(*args, **kwargs)
