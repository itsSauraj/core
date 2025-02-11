from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from admin_panel.services.trainee.service import TraineeCourseServices

from .models import User

@receiver(post_save, sender=User)
def user_created(sender, instance, created, **kwargs):    
  if created and kwargs.get('groups') is not None:
    if isinstance(kwargs.get('groups'), list) or isinstance(kwargs.get('groups'), str):
      if "Trainee" in kwargs.get('groups'):
        assineee = kwargs.get('assignee')
        context_data = {
          "user": instance,
          "collection": [assineee.default_collection.id],
        }
        TraineeCourseServices.create(assineee, context_data)

@receiver(pre_delete, sender=User)
def user_deleted(sender, instance, **kwargs):  
  instance.groups.clear()
  
  instance.username = f"deleted_{instance.username}_{instance.id}"
  instance.email = f"deleted_{instance.email}_{instance.id}"
  instance.employee_id = f"deleted_{instance.employee_id}_{instance.id}"

  instance.save()

