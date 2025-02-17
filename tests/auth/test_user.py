# test_api.py
import pytest
from django.urls import reverse
from rest_framework import status
from admin_panel.models import User
import os
from dotenv import load_dotenv

load_dotenv('.env.test')

username = os.getenv('TEST_USERNAME', None)
password = os.getenv('TEST_PASSWORD', None)

from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_user_register(client):
  register = {
    'username': 'testuser',
    'email': 'testuser@example.com',
    'password': 'Test@1234',
    'confirm_password': 'Test@1234',
    'role': 'trainee',
    'first_name': 'Test',
    'last_name': 'User',
  }

  register_url = '/api/auth/user/'

  response = client.post(register_url, register, format='json')

  assert response.status_code == status.HTTP_201_CREATED, "User created"
  user = User.objects.get(username='testuser')
  user.delete()