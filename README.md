# Training Management Platform

A comprehensive platform for managing trainees, courses, and assessments while facilitating effective communication and collaboration among trainees, mentors, and administrators.

[![API Documentation](https://img.shields.io/badge/API%20Docs-Postman-orange)](https://documenter.getpostman.com/view/28728365/2sAYXFjdCz)
[![Python](https://img.shields.io/badge/Python-3.12-blue)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-Latest-092E20)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-Latest-red)](https://redis.io/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue)](https://www.docker.com/)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=fff)](https://www.docker.com/)
[![Git](https://img.shields.io/badge/Git-F05032?logo=git&logoColor=fff)](https://git-scm.com/downloads)

## Features

- User Management (Trainees, Mentors, Administrators)
- Course Management and Progress Tracking
- Assessment and Evaluation System
- Real-time Communication via WebSockets
- Role-based Access Control
- Soft Delete Support
- Background Task Processing

## Tech Stack

### Backend
- Python (v3.12.x)
- Django & Django REST Framework
- JWT Authentication
- Django Channels (WebSocket Support)
- Django Softdelete
- PostgreSQL (Database)
- Redis (Cache & Message Broker)
- Docker & Docker Compose

## Prerequisites

- Python 3.12 or higher
- PostgreSQL
- Redis (for WebSocket and background tasks)
- Docker and Docker Compose (optional)

## Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   .\venv\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Setup**
   ```bash
   cp .env.example .env
   # Update .env with your configuration
   ```

5. **Database Setup**
   ```bash
   python manage.py migrate
   python manage.py setup_permissions
   python manage.py setup_roles
   ```

6. **Run Development Server**
   
   Standard Django Server:
   ```bash
   python manage.py runserver
   ```

   With WebSocket Support:
   ```bash
   daphne -b 0.0.0.0 -p 8000 core.asgi:application
   ```

## Docker Deployment

### Using Docker

1. **Build the Image**
   ```bash
   docker build -t core-app .
   ```

2. **Run the Container**
   ```bash
   docker run -d -p 8000:8000 --name core-app-container core-app
   ```

### Using Docker Compose

1. **Start Services**
   ```bash
   docker-compose up --build
   ```

2. **Run Migrations**
   ```bash
   docker-compose exec web python manage.py migrate
   docker-compose exec web python manage.py setup_permissions
   docker-compose exec web python manage.py setup_roles
   ```

## API Documentation

Comprehensive API documentation is available on Postman:
[API Documentation](https://documenter.getpostman.com/view/28728365/2sAYXFjdCz)

## Running Tests ![](https://img.shields.io/badge/inbeta-red) ![](https://img.shields.io/badge/inprogress-blue)



Writing the test case in under beta

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_file.py

# Run with coverage report
pytest --cov=.
```

## Common Issues & Troubleshooting

1. **Database Connection Issues**
   - Verify PostgreSQL is running
   - Check database credentials in .env
   - Ensure database exists

2. **WebSocket Connection Issues**
   - Verify Redis is running
   - Check Redis connection settings
   - Ensure proper ASGI setup

## License

This project is licensed under the MIT License - see the [LICENSE.rst](LICENSE.rst) file for details.