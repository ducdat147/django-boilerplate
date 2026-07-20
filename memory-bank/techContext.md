# Technical Context

## Technologies Used

### Backend

| Technology | Version | Purpose       |
| ---------- | ------- | ------------- |
| Python     | 3.13+   | Runtime       |
| Django     | 5.2+    | Web framework |
| DRF        | Latest  | REST API      |
| PostgreSQL | Latest  | Database      |
| Redis      | Latest  | Cache/Broker  |
| Celery     | Latest  | Task queue    |
| uWSGI      | Latest  | WSGI server   |

### Frontend

| Technology      | Purpose  |
| --------------- | -------- |
| Tailwind CSS v4 | Styling  |
| Django Unfold   | Admin UI |

### DevOps & Observability

| Tool          | Purpose             |
| ------------- | ------------------- |
| Docker        | Containerization    |
| Grafana       | Visualization       |
| Loki          | Log aggregation     |
| Tempo         | Distributed tracing |
| OpenTelemetry | Instrumentation     |

## Development Setup

```bash
# Initialize project
make init

# Install dependencies (dev)
make install.dev

# Run development server
make run  # http://localhost:80
```

## Technical Constraints

- Python 3.13+ required
- PostgreSQL required (no SQLite support intended)
- Docker recommended for full observability stack

## Dependencies

- **Package Management**: uv (Python), pnpm (Node.js)
- **Code Quality**: Ruff, pre-commit
- **Testing**: pytest, pytest-django, pytest-cov

## Tool Usage Patterns

- `make test` - Run full test suite
- `make lint` - Run Ruff linter
- `make docker.up` - Start Docker stack
- `make migrate` - Apply migrations
