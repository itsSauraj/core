# Overview

This project is a comprehensive platform for managing trainees, courses, and assessments while facilitating effective communication and collaboration among trainees, mentors, and administrators. It focuses on tracking course progress, conducting evaluations, and providing feedback.

# Tech Stack

* Backend
  * Python (v3.13.x)
  * Django
  * RestFramework
  * RestframeFrameWork Simple JWT
  * PostgresSQL

# How to run

##### Follow the commands in order

1. First Create a python3 virtual environment
2. Start the virtual environment
3. Now follow the commands
  * `pip install -r requirements.txt`
  * `python manage.py migrate`
  * `python manage.py setup_permissions`
  * `python manage.py setup_roles`
4. After that to the application run
  * `python manage.py runserver`
  
