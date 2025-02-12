from django.conf import settings
from datetime import datetime, timezone
import hashlib
import base64
from cryptography.fernet import Fernet, InvalidToken
from django.core.exceptions import ValidationError

from admin_panel.models import User

class PasswordResetTokenHandler:

  @classmethod
  def generate_token(cls, user):
    try:
      key = base64.urlsafe_b64encode(
        hashlib.sha256(settings.SECRET_KEY.encode()).digest()
      )
      f = Fernet(key)
      timestamp = int(datetime.now(timezone.utc).timestamp())
      message = f"{user.id}:{user.email}:{user.password}:{timestamp}"
      return f.encrypt(message.encode()).decode()
    except Exception as e:
      raise ValidationError(f"Error generating token: {str(e)}")

  @classmethod
  def validate_token(cls, token):
    max_age_minutes = int(settings.PASSWORD_RESET_TOKEN_MAX_AGE.encode('utf-8'))
    try:
      key = base64.urlsafe_b64encode(
        hashlib.sha256(settings.SECRET_KEY.encode()).digest()
      )
      f = Fernet(key)
      decrypted = f.decrypt(token.encode()).decode()
      user_id, email, password_hash, timestamp = decrypted.split(':')
      age = datetime.now(timezone.utc).timestamp() - int(timestamp)
      if age > (max_age_minutes * 60):
        return False, None, "Token has expired"
      try:
        user = User.objects.get(id=user_id)
        if user.email != email:
          return False, None, "Email has changed since token was issued"
        if user.password != password_hash:
          return False, None, "Password has been changed since token was issued"
        return True, user, None
      except User.DoesNotExist:
        return False, None, "User not found"
    except InvalidToken:
      return False, None, "Invalid or corrupted token"
    except Exception as e:
      return False, None, f"Error validating token: {str(e)}"

  @classmethod
  def get_user_from_token(cls, token):
    is_valid, user, _ = cls.validate_token(token)
    return user if is_valid else None

tokenization = PasswordResetTokenHandler()