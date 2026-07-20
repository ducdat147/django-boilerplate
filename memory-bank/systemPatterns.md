# System Patterns

## Architecture Overview

```
├── configurations/     # Project configuration (settings, URLs, middleware)
├── core/              # Django apps (user, common)
├── common/            # Shared utilities (models, exceptions, tasks)
├── utils/             # Helper functions
├── tests/             # Test suite (unit, integration)
├── templates/         # Django templates
└── bash/              # Scripts for DevOps
```

## Key Technical Decisions

### Settings Structure

- `configurations/settings/base.py` - Shared settings
- `configurations/settings/local.py` - Development overrides
- `configurations/settings/production.py` - Production overrides
- `configurations/settings/packages/` - Per-package configs

### API Architecture

- Django REST Framework for API development
- drf-spectacular for OpenAPI 3.0 schema generation
- JWT authentication via djangorestframework-simplejwt

### Database Patterns

- PostgreSQL with psycopg3
- Abstract base models in `common/models.py`
- Django Simple History for audit trails

## Design Patterns in Use

1. **Repository Pattern**: Via Django ORM
2. **Abstract Base Models**: `common/models.py` for shared fields
3. **Serializer Layer**: DRF serializers for data transformation
4. **Celery Tasks**: For async operations in `common/tasks.py`

## Component Relationships

```
core/user/ → common/models.py (inheritance)
configurations/ → core/*/urls.py (URL routing)
tests/ → core/*/ (testing coverage)
```

## Critical Implementation Paths

- Authentication: `core/user/views/` → JWT tokens
- API Documentation: drf-spectacular auto-generation
- Background Tasks: Celery workers with RabbitMQ/Redis
