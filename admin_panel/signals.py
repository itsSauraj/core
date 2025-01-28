from django.db.models.signals import post_save
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
