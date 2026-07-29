# Django Boilerplate

![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)![Django 5.2+](https://img.shields.io/badge/django-5.2+-green.svg)![Tests](https://img.shields.io/badge/tests-12%20passed-success.svg)![Coverage](https://img.shields.io/badge/coverage-52.20%25-yellow.svg)![Code style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)## Introduction

A modern Django boilerplate project with best practices, pre-configured packages, and observability tools for rapid development and production-ready applications.

## Features

### Core Features

- **Modular Settings Structure**: Separate configurations for development, production, and base settings
- **Modern Package Management**: Using `uv` for fast Python dependency management and `pnpm` for frontend packages
- **Docker Support**: Full Docker Compose setup for both local development and production environments
- **Authentication & Authorization**:
  - Django Allauth for comprehensive authentication
  - Django Guardian for object-level permissions
  - JWT support with djangorestframework-simplejwt
  - Two-factor authentication with PyOTP and QR codes
- **API Development**:
  - Django REST Framework for building robust APIs
  - drf-spectacular for automatic OpenAPI schema generation
  - CORS support with django-cors-headers

### Pre-configured Packages

- **Admin Interface**: Django Unfold for modern, enhanced admin UI
- **Asynchronous Tasks**: Celery with Redis/RabbitMQ broker and django-celery-beat for scheduled tasks
- **Database**: PostgreSQL with psycopg3
- **Internationalization**: Django Modeltranslation for multilingual content support
- **Data Management**:
  - Django Money for handling monetary values
  - Django Phonenumber Field for phone number validation
  - Django Import/Export for data import/export functionality
  - Django Simple History for model change tracking
  - Django Filter for advanced filtering
- **Dynamic Configuration**: Django Constance for runtime settings management
- **Security**: Cryptography library for secure operations
- **UI**: Tailwind CSS v4 integration for modern, responsive design

### Observability & Monitoring

- **Distributed Tracing**: OpenTelemetry integration for Django, Celery, and ASGI
- **Logging**: JSON structured logging with Grafana Loki
- **Metrics & Visualization**: Grafana dashboards
- **Tracing Backend**: Grafana Tempo for distributed tracing
- **Task Monitoring**: Flower for Celery task monitoring

### Development Tools

- **Pre-commit Hooks**: Automated code quality checks
- **Code Formatting**: Ruff for linting and formatting
- **Testing**: pytest with pytest-django, pytest-cov, pytest-mock, and pytest-xdist
- **Static Files**: Whitenoise for efficient static file serving
- **WSGI Server**: uWSGI for production deployment

## Getting Started

### Prerequisites

- Python 3.13 or higher
- Node.js and pnpm
- Docker and Docker Compose (optional, for containerized development)
- PostgreSQL (if running without Docker)
- Redis (if running without Docker)

### Local Development Setup

 1. **Clone the repository:**

    ```bash
    git clone https://github.com/ducdat147/django-boilerplate.git .
    ```

 2. **Install uv (if not already installed):**

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

 3. **Initialize the project:**

    ```bash
    make init
    ```

 4. **Install dependencies:**

    For development (includes dev dependencies):

    ```bash
    make install.dev
    ```

    For production:

    ```bash
    make install
    ```

 5. **Set up environment variables:**

    ```bash
    cp .example.env.host .env.host
    # Edit .env.host file with your configuration (used by host commands: make run, make test, make migrate...)
    ```

 6. **Apply database migrations:**

    ```bash
    make migrate
    ```

 7. **Create a superuser:**

    ```bash
    make user
    # Default: username=admin, email=admin@admin.com
    ```

 8. **Seed initial data (optional):**

    ```bash
    make seed_data
    ```

 9. **Compile static files:**

    ```bash
    make collectstatic
    ```

10. **Start the development server:**

    ```bash
    make run
    # Server will be available at http://localhost:80
    ```

### Docker Development Setup

1. **Start all services with Docker Compose:**

   ```bash
   make docker.up
   ```

   This will start:

   - Django application
   - PostgreSQL database
   - Redis cache
   - RabbitMQ message broker
   - Grafana (http://localhost:3000)
   - Tempo (distributed tracing)

2. **Stop all services:**

   ```bash
   make docker.down.local
   ```

### Production Deployment

1. **Deploy to production:**

   ```bash
   make deploy
   ```

   This will:

   - Start the production Docker Compose stack
   - Open the application at http://localhost/
   - Open Grafana at http://localhost:3000/

## Available Makefile Commands

### Setup & Installation

- `make init`: Initialize the project (create logs directory)
- `make install.dev`: Install all dependencies including dev dependencies and setup pre-commit hooks
- `make install`: Install production dependencies and setup pre-commit hooks
- `` ` ``: Update all Python and Node.js packages to latest versions

### Development

- `make run`: Start the Django development server (http://localhost:80)
- `make shell`: Open Django shell
- `make seed_data`: Seed the database with initial data
- `make app <app_name>`: Create a new Django app in the `core/` directory

### Database

- `make migrations`: Create new database migrations
- `make migrate`: Apply database migrations (also runs makemigrations)
- `make clear-migrations`: Delete all migrations and recreate them

### User Management

- `make user`: Create a superuser (admin/admin@admin.com)

### Internationalization

- `make message`: Generate translation message files for English and Vietnamese
- `make compile`: Compile translation messages

### Static Files

- `make css`: Compile Tailwind CSS
- `make collectstatic`: Compile CSS and collect all static files

### Code Quality

- `make lint`: Run Ruff linter and formatter
- `make pre-commit`: Run all pre-commit hooks
- `make pyc`: Clean Python cache files

### Testing

- `make test`: Run all tests with pytest and coverage
- `make test.unit`: Run only unit tests
- `make test.integration`: Run only integration tests
- `make test.fast`: Run tests, skipping slow tests
- `make test.coverage`: Generate detailed HTML coverage report
- `make test.parallel`: Run tests in parallel for faster execution
- `make test.verbose`: Run tests with verbose output
- `make test.failed`: Re-run only previously failed tests
- `make test.file <path>`: Run tests in a specific file
- `make test.django`: Run legacy Django tests (deprecated)
- `make test.django.report`: Show Django test coverage report
- `make test.django.html`: Generate Django test HTML coverage report

### Celery

- `make celery`: Start Celery worker with threads pool

### Package Management

- `make i <package_name>`: Install a new Python package
- `make i.dev <package_name>`: Install a new dev Python package
- `make r <package_name>`: Remove a Python package
- `make r.dev <package_name>`: Remove a dev Python package

### Docker

- `make docker.up`: Start local development environment with Docker Compose
- `make docker.down.local`: Stop local Docker environment
- `make docker.down.prod`: Stop production Docker environment
- `make docker.build`: Build Docker image
- `make docker.push`: Build and push Docker image to registry
- `make deploy`: Deploy production environment
- `make prune`: Remove all stopped containers and unused images

### Git Workflow

- `make git.develop`: Checkout and pull the latest develop branch
- `make git.clean`: Delete all local branches except develop
- `make git.createbranch <branch_name>`: Create a new feature branch from develop

### Maintenance

- `make clean`: Run CSS compilation, message generation, pyc cleanup, and pre-commit hooks

## Project Structure

```
├── bash/                     # Shell scripts for development and deployment
│   ├── devops/               # DevOps configuration files
│   │   ├── alloy/            # Grafana Alloy configuration (log shipping + OTel collector)
│   │   ├── grafana/          # Grafana datasources + alerting provisioning
│   │   ├── loki/             # Loki logging configuration
│   │   ├── nginx/            # Nginx configuration
│   │   ├── prometheus/       # Prometheus scrape configuration
│   │   ├── rabbitmq/         # RabbitMQ enabled_plugins (management + prometheus)
│   │   └── tempo/            # Tempo tracing configuration
│   └── django/               # Django entrypoint and startup scripts
│       ├── celery/           # Celery worker, beat, and flower scripts
│       └── entrypoint, start
├── common/                   # Shared utilities across the project
│   ├── encoders.py           # Custom JSON encoders
│   ├── exceptions.py         # Custom exception classes
│   ├── forms.py              # Common form classes
│   ├── models.py             # Abstract base models
│   └── tasks.py              # Shared Celery tasks
├── configurations/            # Project configuration
│   ├── settings/             # Modular settings
│   │   ├── base.py           # Base settings
│   │   ├── local.py          # Development settings
│   │   ├── production.py     # Production settings
│   │   └── packages/         # Package-specific configurations
│   ├── celery.py             # Celery configuration
│   ├── logging.py            # Logging configuration
│   ├── middleware.py         # Custom middleware
│   ├── telemetry.py          # OpenTelemetry configuration
│   ├── urls.py               # Main URL configuration
│   └── wsgi.py, asgi.py      # WSGI/ASGI applications
├── core/                     # Core Django apps
│   ├── common/               # Common app for shared functionality
│   └── user/                 # User management app
│       ├── admin.py          # Admin customizations
│       ├── enums.py          # Enumerations
│       ├── models.py         # User models
│       ├── serializers/      # DRF serializers
│       ├── urls/             # URL routing
│       └── views/            # Views and API endpoints
├── locale/                   # Internationalization files (en, vi)
├── logs/                     # Application logs
├── media/                    # User-uploaded media files
├── resources/                # Static resources
├── staticfiles/               # Collected static files
├── templates/                # Django templates
│   ├── admin/                # Custom admin templates
│   └── emails/               # Email templates
├── tests/                    # Test suite
│   ├── conftest.py           # Pytest fixtures and configuration
│   ├── mixins.py             # Reusable test mixins
│   ├── unit/                 # Unit tests
│   │   ├── models/           # Model tests
│   │   ├── views/            # View/API tests
│   │   └── serializers/      # Serializer tests
│   ├── integration/          # Integration tests
│   │   └── test_auth_flow.py # Authentication flow tests
│   ├── test_auth.py          # Legacy auth tests (deprecated)
│   ├── test_user.py          # Legacy user tests (deprecated)
│   └── test_case/            # Test case data (JSON, deprecated)
├── utils/                    # Utility functions
│   ├── auth.py               # Authentication utilities
│   ├── crypto.py             # Cryptography utilities
│   └── performs.py           # Performance utilities
├── docker-compose.local.yml  # Local development Docker setup
├── docker-compose.prod.yml   # Production Docker setup
├── Dockerfile                 # Docker image definition
├── makefile                   # Development commands
├── manage.py                 # Django management script
├── package.json              # Node.js dependencies (Tailwind CSS)
├── pyproject.toml            # Python project configuration and dependencies
├── style.css                 # Tailwind CSS input file
└── uwsgi.ini                 # uWSGI configuration
```

## Technology Stack

### Backend

- **Framework**: Django 5.2+
- **Python**: 3.13+
- **Database**: PostgreSQL with psycopg3
- **Cache & Message Broker**: Redis, RabbitMQ
- **Task Queue**: Celery with django-celery-beat
- **API**: Django REST Framework with drf-spectacular
- **WSGI Server**: uWSGI

### Frontend

- **CSS Framework**: Tailwind CSS v4
- **Admin UI**: Django Unfold

### DevOps & Observability

- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx
- **Logging**: Grafana Loki + Promtail
- **Tracing**: Grafana Tempo with OpenTelemetry
- **Visualization**: Grafana
- **Task Monitoring**: Flower

### Development Tools

- **Package Manager**: uv (Python), pnpm (Node.js)
- **Code Quality**: Ruff, pre-commit hooks
- **Testing**: pytest, pytest-django, pytest-cov, pytest-mock, pytest-xdist

## Configuration

### Environment Variables

Create a `.env.host` file based on `.example.env.host` with the following key variables (used when running commands directly on the host, e.g. `make run`, `make test`, `make migrate`; containers use their own `.env`, not tracked in git):

- **Django Settings**: `DJANGO_SETTINGS_MODULE`, `SECRET_KEY`, `DEBUG`
- **Database**: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`
- **Redis**: Redis connection settings
- **Celery**: Broker and backend URLs
- **Email**: SMTP configuration
- **OpenTelemetry**: Tracing endpoints

### Settings Modules

- `configurations.settings.local`: Development environment
- `configurations.settings.production`: Production environment
- `configurations.settings.base`: Shared base settings

## Testing

This project uses **pytest** with a comprehensive testing framework designed for Django applications.

### Quick Start

Run all tests:

```bash
make test
```

Run specific test types:

```bash
make test.unit         # Unit tests only (fast, isolated)
make test.integration  # Integration tests (complete workflows)
make test.fast         # Skip slow tests
```

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures (api_client, user, authenticated_client, etc.)
├── mixins.py                # Reusable test mixins (APITestMixin, CRUDTestMixin, etc.)
├── unit/                    # Unit tests (70% of test suite)
│   ├── models/              # Model tests
│   ├── views/               # API endpoint tests
│   │   └── test_user_views.py
│   └── serializers/         # Serializer tests
└── integration/             # Integration tests (25% of test suite)
    └── test_auth_flow.py    # Complete authentication workflows
```

### Available Test Commands

```bash
# Run all tests with coverage
make test

# Run specific test types
make test.unit              # Unit tests only
make test.integration       # Integration tests only
make test.fast              # Skip slow tests (@pytest.mark.slow)

# Coverage reports
make test.coverage          # Detailed HTML coverage report (opens in browser)

# Advanced options
make test.parallel          # Run tests in parallel (faster)
make test.verbose           # Verbose output with detailed info
make test.failed            # Re-run only failed tests
make test.file tests/unit/views/test_user_views.py  # Run specific file
```

### Test Coverage

Current coverage: **52.20%** (Target: 80%+)

View detailed coverage report:

```bash
make test.coverage
# Opens htmlcov/index.html in browser
```

### Writing Tests

#### Example Unit Test

```python
# tests/unit/views/test_user_views.py
import pytest
from rest_framework import status
from django.urls import reverse

@pytest.mark.unit
class TestUserProfileView:
    """Test user profile view endpoints."""

    @pytest.fixture
    def url(self):
        return reverse("user:my_profile")

    def test_get_profile_authenticated(self, authenticated_client, verified_user, url):
        """Test getting profile with authentication."""
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == verified_user.username
```

#### Example Integration Test

```python
# tests/integration/test_auth_flow.py
import pytest
from rest_framework import status

@pytest.mark.integration
class TestAuthenticationFlow:
    """Test complete authentication flow."""

    def test_complete_registration_login_flow(self, api_client, db):
        """Test user registration and login."""
        # Step 1: Register
        register_url = reverse("auth:register")
        register_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "phone": "+84369000001",
        }
        response = api_client.post(register_url, register_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        # Step 2: Login
        login_url = reverse("auth:token_obtain_pair")
        login_data = {"username": "newuser", "password": "SecurePass123!"}
        response = api_client.post(login_url, login_data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
```

### Available Fixtures

Defined in `tests/conftest.py`:

- `api_client`: Unauthenticated DRF APIClient
- `user`: Basic test user (username: testuser, password: testpass123)
- `verified_user`: User with profile created
- `admin_user`: Admin user with superuser privileges
- `authenticated_client`: APIClient with JWT authentication (uses `verified_user`)
- `admin_client`: APIClient authenticated as admin

### Testing Best Practices

1. **Follow AAA Pattern**: Arrange, Act, Assert
2. **Use Descriptive Names**: `test_create_user_with_valid_data_succeeds()`
3. **Leverage Fixtures**: Reuse setup code via pytest fixtures
4. **Parametrize Tests**: Use `@pytest.mark.parametrize` for variations
5. **Mark Tests Properly**:
   - `@pytest.mark.unit` - Fast, isolated unit tests
   - `@pytest.mark.integration` - Multi-component integration tests
   - `@pytest.mark.slow` - Tests that take &gt;1 second
   - `@pytest.mark.e2e` - End-to-end tests

### Documentation

For detailed testing guidelines, see:

- `tests/TESTING_STANDARDS.md`: Comprehensive 60+ page testing guide
- `tests/QUICK_START.md`: Quick start guide for writing tests
- `tests/ANALYSIS_REPORT.md`: Analysis of current testing approach

### Migration from Legacy Tests

Legacy JSON-based tests in `tests/test_auth.py` and `tests/test_user.py` are deprecated. New tests should follow the pytest approach outlined in the testing standards documentation.

## Monitoring & Observability

Access monitoring tools when running with Docker:

- **Grafana**: http://localhost:3000 (visualization and dashboards)
- **Flower**: Celery task monitoring (configured in your setup)
- **Tempo**: http://localhost:3200 (distributed tracing)

All Django, Celery, and ASGI requests are automatically instrumented with OpenTelemetry for distributed tracing.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch from `develop`:

   ```bash
   make git.createbranch your-feature-name
   ```
3. Make your changes and commit them
4. Run code quality checks:

   ```bash
   make lint
   make pre-commit
   ```
5. Run tests to ensure everything works:

   ```bash
   make test
   ```
6. Push to your fork and submit a pull request

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author

**ducdat147** - [GitHub Profile](https://github.com/ducdat147)
