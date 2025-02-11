from django.contrib.auth.models import Group
from django.db.models.signals import post_save

from admin_panel.models import User
from admin_panel.services.user.serializer import UserSerializer
from admin_panel.services.mailer.factory import mailer

from admin_panel.services.course.default import default_course, default_collection
from admin_panel.services.course.service import CourseAPIService
from admin_panel.services.course.course_collection import CourseCollectionAPIService

class UserAPIService:

  @staticmethod
  def get_user_by_id(id):
    return User.objects.get(id=id)
  
  @staticmethod
  def get_user_by_email(email):
    return User.objects.get(email=email)
  
  @staticmethod
  def get_user_by_username(username):
    return User.objects.get(username=username)
  
  @staticmethod
  def get_user_mentors(user_id):
    return UserAPIService.get_user_by_id(user_id).get_created_mentors()
  
  @staticmethod
  def get_trainee(pk, user):
    return User.objects.get(id=pk, created_by=user)

  @staticmethod
  def get_user_trainees(user_id):
    return UserAPIService.get_user_by_id(user_id).get_created_trainees()
  
  @staticmethod
  def get_all_trainees():
    return User.objects.filter(groups__name='Trainee')
  
  @staticmethod
  def get_created_courses(user_id):
    return UserAPIService.get_user_by_id(user_id).get_created_courses()
  
  @staticmethod
  def get_created_collections(user_id):
    return UserAPIService.get_user_by_id(user_id).get_created_collections()
  
  @staticmethod
  def add_user_to_group(user, group, many=False):
    if many:
      for group_name in group:
        user.groups.add(Group.objects.get(name=group_name))
    else:
      user.groups.add(Group.objects.get(name=group))
    user.save()

  @staticmethod
  def remove_dublicate_values(user_id, data):
    user = UserAPIService.get_user_by_id(user_id)
    unchanged_data = {}
    for key, value in data.items():
      if value != getattr(user, key):
        unchanged_data[key] = value
    return unchanged_data

  @staticmethod
  def create(request, data, group=[]):

    user_permissions = request.user.get_all_permissions()
    required_permissions = ['custom_permission.mentors.create', 'custom_permission.trainees.create']

    serializer = UserSerializer(data)

    if 'Admin' not in group and not all(permission in user_permissions for permission in required_permissions):
        raise PermissionError('You do not have permission to create a user')

    try:
      user = User.objects.create_user(**serializer.data)
    except Exception as e:
      return False
    post_save.send(sender=User, instance=user, created=True, groups=group, assignee=request.user)

    if 'Admin' in group:
      mailer.send_mail(
        'send_user_verification_email',
        user_id=user.id
      )
    
    UserAPIService.add_user_to_group(user, group)

    if 'Admin' not in group:
      user.created_by = request.user
      user.save()

    course = CourseAPIService.import_course(request, default_course, user=user)
    default_collection['courses'] = [course.id]
    collection = CourseCollectionAPIService.create(request, default_collection, user=user)
    CourseCollectionAPIService.set_default_collection(request, collection, user=user)
      
    return user
  
  @staticmethod
  def update(request, data, user_id):

    user = UserAPIService.get_user_by_id(user_id)

    for key, value in data.items():
      setattr(user, key, value)
    user.save()

    return user

  @staticmethod
  def delete(request, user_id, many=False):
    if many:
      User.objects.filter(id__in=user_id).delete()
    else:
      UserAPIService.get_user_by_id(user_id).delete()

    return True