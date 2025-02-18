import pytest
import os
from rest_framework.test import APIClient
from dotenv import load_dotenv
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

load_dotenv('.env.test')

username = os.getenv('TEST_USERNAME', None)
password = os.getenv('TEST_PASSWORD', None)

def pytest_configure():
  load_dotenv('.env.test')

@pytest.fixture(scope='session')
def django_db_setup():
  from django.conf import settings
  settings.DATABASES['default'] = {
    'ENGINE': os.getenv('DATABASE_BACKEND', 'django.db.backends.postgresql'),
    'NAME': os.getenv('DATABASE_NAME', 'test_db'),
    'USER': os.getenv('DATABASE_USER', 'postgres'),
    'PASSWORD': os.getenv('DATABASE_PASSWORD', ''),
    'HOST': os.getenv('DATABASE_HOST', 'localhost'),
    'PORT': os.getenv('DATABASE_PORT', '5432'),
    'ATOMIC_REQUESTS': False,
  }

@pytest.fixture
def api_client():
  register = {
    'username': 'testuser',
    'email': 'testuser@example.com',
    'password': 'Test@1234',
    'confirm_password': 'Test@1234',
    'role': 'trainee',
    'first_name': 'Test',
    'last_name': 'User',
  }
  register_url = "/api/auth/user/"
  url = reverse('user_login')
  client = APIClient()

  created_response = client.post(
    register_url,
    register,
    format='json'
  )

  assert created_response.status_code == 201

  response = client.post(
    url,
    {
      'username': 'testuser',
      'password': 'Test@1234'
    },
    format='json'
  )

  assert response.status_code == 200

  token = response.data['token']
  client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
  return client

@pytest.fixture
def client():
  return APIClient()