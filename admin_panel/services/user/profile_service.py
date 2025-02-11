from django.db.models.signals import post_save, pre_delete

from admin_panel.models import User
from admin_panel.services.user.serializer import UserSerializer
from admin_panel.services.mailer.factory import mailer
from admin_panel.services.TOTPService import verify_otp_by_key

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

  @staticmethod
  def delete_account(user):  
    user_id = user.id
    mailer.send_mail(
      'send_user_account_deleted_notification',
      user_id=user_id
    )
    user.delete()


  @staticmethod
  def verify_account(user_id, otp):

    user = User.objects.get(pk=user_id)

    if verify_otp_by_key(user.id, otp):
      user.is_verified = True
      user.save()

      return user
    return False