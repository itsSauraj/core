import uuid
from datetime import timedelta, datetime, timezone

from django.db import models
from django.contrib.auth.models import AbstractUser, Group

from django.db.models.signals import pre_delete, post_delete

from admin_panel.manager import CustomUserManager

from django_softdelete.models import SoftDeleteModel
from django.contrib.contenttypes.fields import GenericRelation
from django.db import transaction

from .utils import rename_file

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
  phone_number = models.CharField(('phone number'),max_length=15, null=True, blank=True)
  birth_date = models.DateField(('birth date'), null=True, blank=True)
  address = models.TextField(('address'), null=True, blank=True)
  employee_id = models.CharField(('employee id'), max_length=255, null=True, blank=True, unique=True)
  joining_date = models.DateField(('joining date'), null=True, blank=True)

  email = models.EmailField(("email address"), unique=True)

  created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='creator')

  enrolled_collections = models.ManyToManyField('CourseCollection', related_name='enrolled_users', blank=True)
  default_collection = models.ForeignKey('CourseCollection', on_delete=models.SET_NULL, null=True, blank=True, related_name='default_user')

  objects = CustomUserManager()

  def __str__(self):
    return self.username
  
  def save(self, *args, **kwargs):
    if not self.pk:  # Check if the user is being created
      self.set_password(self.password)  # Hash the password

    if self.created_by is not None:
      get_default_collection = self.created_by.default_collection
      self.enrolled_collections.add(get_default_collection)
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
    return self.course.all()
  
  # Get all collections of the user
  def get_created_collections(self):
    return self.collections.all()

  # Get all collections coures of the user
  def get_enrolled_courses_list(self):
    collections = self.enrolled_courses.all()
    courses_list = [
      course for collection in collections for course in collection.collection.courses.all()
    ]
    return courses_list

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
  
  def get_all_lessons(self):
    return self.lessons.all().order_by('sequence')
  
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


class CourseCollection(BaseModel):
  title = models.CharField(('collection title'), max_length=255, null=False, blank=False)
  description = models.TextField(('collection description'), null=True, blank=True)
  courses = models.ManyToManyField(Course, related_name='collections', blank=True)
  image = models.ImageField(upload_to=rename_file, null=True, blank=True)
  alloted_time = models.IntegerField(('alloted time'), blank=False, null=False) # Alloted time in hours
  
  created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='collections')

  def __str__(self):
    return self.title
  
  def save(self, *args, **kwargs):
    super(CourseCollection, self).save(*args, **kwargs)

  @property
  def get_all_courses(self):
    return self.courses.all()
  
  @property
  def is_default(self):
    return self.created_by.default_collection == self


class UserCoursesEnrolled(BaseModel):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrolled_courses')
  collection = models.ForeignKey(CourseCollection, on_delete=models.CASCADE)
  enrolled_on = models.DateTimeField(('enrolled on'), auto_now_add=True)
  started_on = models.DateTimeField(('started on'), null=True, blank=True)
  completed_on = models.DateTimeField(('completed on'), null=True, blank=True)
  is_completed = models.BooleanField(('completed'), default=False)

  assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_courses')

  def __str__(self):
    return f"{self.user.username} - {self.collection.title}"

  def save(self, *args, **kwargs):
    super(UserCoursesEnrolled, self).save(*args, **kwargs)

class UserCourseActivity(BaseModel):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_activity')
  course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='user_activity')
  started_on = models.DateTimeField(('started on'), auto_now_add=True)
  completed_on = models.DateTimeField(('completed on'), null=True, blank=True)

  def __str__(self):
    return f"{self.user.username} - {self.course.title} - {self.started_on} - {self.completed_on}"
  
  def is_started(self):
    return self.started_on is not None
  
  def is_completed(self):
    return self.completed_on is not None

class UserCourseProgress(BaseModel):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='course_progress')
  course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='user_progress')
  module = models.ForeignKey(CourseModules, on_delete=models.CASCADE, null=True, blank=True, related_name='user_progress')
  lesson = models.ForeignKey(CourseModuleLessons, on_delete=models.CASCADE, null=True, blank=True, related_name='user_progress')
  completed_on = models.DateTimeField(('completed on'), auto_now_add=True)

  def __str__(self):
    try:
      return f"{self.user.username} - {self.course.title} - {self.module.title} - {self.lesson.title}"
    except:
      return f"{self.user.username} - {self.course.title}"
  
  def save(self, *args, **kwargs):
    super(UserCourseProgress, self).save(*args, **kwargs)

  def get_completed_lessons(self, course):
    return self.objects.filter(course=course, completed_on__isnull=False)
  

class Notification(BaseModel):
    NOTIFICATION_TYPES = (
        ('success', 'Success'),
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    )

    sender = models.ForeignKey(User,on_delete=models.CASCADE,related_name='sent_notifications')
    recipient = models.ForeignKey(User,on_delete=models.CASCADE,related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='info')
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient.username} - {self.message[:50]}"