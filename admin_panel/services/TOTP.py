import time
import hashlib

from django_otp.oath import TOTP
from django.conf import settings


class TOTPVerification:

  def __init__(self, key):
    self.key = key
    self.last_verified_counter = -1
    self.verified = False
    self.number_of_digits = 6
    self.token_validity_period = 35000

  def totp_obj(self):
    totp = TOTP(key=self.key,
                step=self.token_validity_period,
                digits=self.number_of_digits)
    totp.time = time.time()
    return totp

  def generate_token(self):
    totp = self.totp_obj()
    token = str(totp.token()).zfill(6)
    return token

  def verify_token(self, token, tolerance=0):
    try:
      token = int(token)
    except ValueError:
      self.verified = False
    else:
      totp = self.totp_obj()
      if ((totp.t() > self.last_verified_counter) and
            (totp.verify(token, tolerance=tolerance))):
        self.last_verified_counter = totp.t()
        self.verified = True
      else:
          self.verified = False
    return self.verified

def generate_key(key):
  return hashlib.sha256(f"{key}{settings.SECRET_KEY}".encode()).hexdigest()

def generate_otp_by_key(key):
  key = generate_key(key) + str(int(time.time()) // 30)
  key = str(key)
  return TOTPVerification(key=key.encode('utf-8')).generate_token()

def verify_otp_by_key(key, otp):
  key = generate_key(key) + str(int(time.time()) // 30)
  key = str(key)
  return TOTPVerification(key=key.encode('utf-8')).verify_token(otp)
