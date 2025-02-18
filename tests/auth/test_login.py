import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
import os
from dotenv import load_dotenv

load_dotenv('.env.test')

username = os.getenv('TEST_USERNAME', None)
password = os.getenv('TEST_PASSWORD', None)

User = get_user_model()

@pytest.mark.django_db
def test_user_login(client):
  login_data = {
    'username': username,
    'password': password
  }

  login_url = reverse('user_login')

  response = client.post(login_url, login_data, format='json')

  assert response.status_code == status.HTTP_200_OK, "User logged in"
  assert 'token' in response.data

@pytest.mark.django_db
def test_invalid_login(client):
  login_data = {
    'username': 'nonexistent',
    'password': 'wrongpass'
  }
  
  login_url = reverse('user_login')
  response = client.post(login_url, login_data, format='json')
  
  assert response.status_code == status.HTTP_400_BAD_REQUEST, response.data

@pytest.mark.django_db
def test_invalid_credentials(client):
  login_data = {
    'username': username,
    'password': 'wrongpass'
  }
  
  login_url = reverse('user_login')
  response = client.post(login_url, login_data, format='json')
  
  assert response.status_code == status.HTTP_400_BAD_REQUEST, response.data