import uuid
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
members_url = reverse('member_user_api')

def create_user(client, type):
  data = {
    "employee_id": 4850,
    "email": "abown4850@nba.com",
    "first_name": "Analiese",
    "last_name": "Meekins",
    "phone_number": "3708902498",
    "joining_date": "2024-12-13",
    "username": "meekini4",
    "password": "Qwe@123",
    "confirm_password": "Qwe@123",
  }
  data = {
    **data,
    "role": type
  }

  response = client.post(members_url, data, format='json')
  return response


@pytest.mark.django_db
def test_create_member_mentor(api_client):
  response = create_user(api_client, 'mentor')
  assert response.status_code == status.HTTP_201_CREATED, response.data
    
  user = User.objects.get(username='meekini4')
  user.delete()

@pytest.mark.django_db
def test_create_member_trainee(api_client):
  response = create_user(api_client, 'trainee')
  assert response.status_code == status.HTTP_201_CREATED, response.data
    
@pytest.mark.django_db  
def test_get_all_mentors(api_client):
  response = api_client.get(reverse('get_all_mentors'))
  assert response.status_code == status.HTTP_200_OK, response.data

@pytest.mark.django_db
def test_get_all_trainees(api_client):
  response = api_client.get(reverse('get_all_trainees'))
  assert response.status_code == status.HTTP_200_OK, response.data

@pytest.mark.django_db
def test_get_trainee_by_id(api_client):
  data = create_user(api_client, 'trainee').data

  response = api_client.get(reverse('member_user_apis', kwargs={'member_id': data['id']}))

  assert response.status_code == status.HTTP_200_OK, response.data
  assert response.data['username'] == 'meekini4'

# wrong data test
@pytest.mark.django_db
def test_get_trainee_by_id_failed(api_client):
  response = api_client.get(reverse('member_user_apis', kwargs={'member_id': uuid.uuid4()}))

  assert response.status_code == status.HTTP_404_NOT_FOUND, response.data