from django.db.models.signals import post_save

from admin_panel.models import User
from admin_panel.services.user.serializer import UserSerializer
from admin_panel.services.mailer.factory import mailer

class ProfileService:
  
  @staticmethod
  def update_profile(user, data):
    for key, value in data.items():
      setattr(user, key, value)
    user.save()

    return user
  
  @staticmethod
  def change_password(user, new_password):
    user.set_password(new_password)
    user.save()

    mailer.send_mail(
      'send_user_password_changed_notification', 
      user_id=user.id
    )