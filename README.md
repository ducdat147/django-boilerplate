# DJANGO Boilerplate

## Introduction
A Django boilerplate project with best practices and commonly used packages pre-configured for rapid development.
## Features
- Modular settings structure for easy environment management (development, production, etc.)
- Pre-configured with popular Django packages:
  - Django REST Framework for building APIs
  - Django Constance for dynamic settings management
  - Django Money for handling monetary values
  - Django Modeltranslation for multilingual support
  - Django Unfold for enhanced admin interface
  - Celery for asynchronous task processing
- Tailwind CSS integration for modern, responsive UI design
- Makefile for common tasks like setup, testing, and linting
- Environment variable management with `.env` files
## Getting Started
1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/django-boilerplate.git .
    ```
2. Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    ```
3. Activate the virtual environment:
    - On Windows:
    ```bash
    .venv\Scripts\activate
    ```
    - On macOS and Linux:
    ```bash
    source .venv/bin/activate
    ```
4. Install the required packages:
    ```bash
    make install
    ```
5. Set up your environment variables:
    - Copy the example environment file and modify it as needed:
    ```bash
    cp .example.env .env
    ```
6. Apply database migrations:
    ```bash
    make migrate
    ```
7. Create a superuser for admin access:
    ```bash
    make user
    ```
8. Start the development server:
    ```bash
    make run
    ```
## Available Makefile Commands
- `make init`: Initialize the project (create logs directory).
- `make install`: Install required Python packages.
- `make migrations`: Create new database migrations based on model changes.
- `make migrate`: Apply database migrations.
- `make staticfiles`: Collect static files.
- `make user`: Create a superuser.
- `make run`: Start the development server.
- `make celery`: Start the Celery worker.
- `make lint`: Run code linters (flake8, isort, black).
- `make test`: Run tests with coverage.
- `make pyc`: Clean up unnecessary files (e.g., `__pycache__`).
- `make i <package_name>`: Install a new package and add it to `requirements.txt`.
- `make docker-up`: Start the development environment using Docker Compose.
- `make docker-down.<prod|local>`: Stop the development environment.
- `make prune`: Remove all stopped containers and unused images.
- `make css`: Compile Tailwind CSS.
- `make app <app_name>`: Create a new Django app.
## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your changes.
## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details
