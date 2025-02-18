# Overview

This project is a comprehensive platform for managing trainees, courses, and assessments while facilitating effective communication and collaboration among trainees, mentors, and administrators. It focuses on tracking course progress and conducting evaluations.

[API Documentation on POSTMAN](https://documenter.getpostman.com/view/28728365/2sAYXFjdCz) is hosted here you can kindly check it out.


# Tech Stack

* __Backend__
  * Python (v3.12.x)
  * Django
  * Django Rest Framework
  * Django Rest Framework Simple JWT
  * Django Softdelete
  * Django Channels
  * PostgreSQL
  * Redis (Background worker)
  * Docker and Docker compose

# How to Run

Follow the commands in order:

1. __Create a Python3 virtual environment__
   ```bash
   python3 -m venv venv
   ```

2. __Activate the virtual environment__
   ```bash
   source venv/bin/activate
   ```

3. __Install dependencies and setup the project__
   ```bash
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py setup_permissions
   python manage.py setup_roles
   ```

4. __Run the application__
   ```bash
   python manage.py runserver
   ```

   __Note:__ To run with WebSocket support, you will need to install Redis for socket layering and run the application using `gunicorn` ASGI or `daphne` ASGI configuration.
   ```bash
   daphne -b 0.0.0.0 -p 8000 core.asgi:application
   ```

5. __For hot reload__
   ```bash
   python server.py
   ```
  # Running with Docker

  To run the application using Docker, follow these steps:

  1. __Build the Docker image__
    ```bash
    docker build -t core-app .
    ```

  2. __Run the Docker container__
    ```bash
    docker run -d -p 8000:8000 --name core-app-container core-app
    ```

  3. __Access the application__
    Open your browser and navigate to `http://localhost:8000`.

  __Note:__ Ensure that Docker is installed and running on your machine before executing these commands.
  # Docker Compose Setup

  To run the application with Docker Compose, follow these steps:

  1. __Ensure you have a `docker-compose.yml` file__ with the necessary configurations for your services (db, redis, web).

  2. __Run the Docker Compose services__
    ```bash
    docker-compose up --build
    ```

  3. __Access the application__
    Open your browser and navigate to `http://localhost:8000`.

  __Note:__ Ensure that Docker and Docker Compose are installed and running on your machine before executing these commands.

For detailed API documentation, please visit the following URLs:

* [API Documentation on POSTMAN](https://documenter.getpostman.com/view/28728365/2sAYXFjdCz)
