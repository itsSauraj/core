import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):

  created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
  updated_at = models.DateTimeField(auto_now=True)
  deleted_at = models.DateTimeField(null=True, blank=True)
  
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  

  created_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='creator')

  def __str__(self):
    return self.username
  
  def save(self, *args, **kwargs):

    print("runneing custom save")
    print(self.pk)

    if not self.pk:  # Check if the user is being created
      self.set_password(self.password)  # Hash the password
    super(User, self).save(*args, **kwargs)