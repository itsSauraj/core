from datetime import datetime, timezone

from django.db.models.signals import post_save, pre_delete
from django.core.exceptions import ValidationError

from admin_panel.models import User
from admin_panel.services.mailer.factory import mailer
from admin_panel.services.Tokenization import tokenization
from admin_panel.services.TOTP import verify_otp_by_key


class ProfileService:
  
  @staticmethod
  def update_profile(user, data):
    for key, value in data.items():
      setattr(user, key, value)
    user.save()

    user.updated_at = datetime.now(tz=timezone.utc)

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
  
  @staticmethod
  def forgot_password(email):
    try:
      user = User.objects.get(email=email)
    except Exception as e:
      return False
    mailer.send_mail(
      'send_user_password_reset_email',
      user_id=user.id
    )
    return user
  
  @staticmethod
  def verify_otp(otp, user_id):
    print(otp)
    print(30 * '-')
    print(user_id)
    return verify_otp_by_key(user_id, otp)
  
  @staticmethod
  def generate_password_reset_token(user_id):
    user = User.objects.get(pk=user_id)
    return tokenization.generate_token(user)
  
  @staticmethod
  def reset_password(token, new_password):

    is_valid, user, error = tokenization.validate_token(token)
    if not is_valid:
      raise ValidationError(error)

    user.set_password(new_password)
    user.save()

    mailer.send_mail(
      'send_user_password_changed_notification', 
      user_id=user.id
    )

    return user