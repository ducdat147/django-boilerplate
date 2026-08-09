FROM python:3.14-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=UTC \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

EXPOSE 8000
EXPOSE 5555

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    build-essential \
    libpq-dev \
    pkg-config \
    gettext \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN addgroup --system django \
    && adduser --system --ingroup django django

COPY ./bash/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint
RUN chown django:django /entrypoint

COPY ./bash/django/start /start-service
RUN sed -i 's/\r$//g' /start-service
RUN chmod +x /start-service
RUN chown django:django /start-service

COPY ./bash/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker
RUN chown django:django /start-celeryworker

COPY ./bash/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat
RUN chown django:django /start-celerybeat

COPY ./bash/django/celery/flower/start /start-celeryflower
RUN sed -i 's/\r$//g' /start-celeryflower
RUN chmod +x /start-celeryflower
RUN chown django:django /start-celeryflower

RUN mkdir /app
RUN mkdir /app/logs
RUN mkdir /app/media
RUN mkdir /app/static
RUN mkdir /app/flower_db
RUN mkdir /var/log/uwsgi

RUN chown -R django:django /app
RUN chown -R django:django /app/logs /var/log/uwsgi

WORKDIR /app

# Copy project and set permissions
COPY . .
RUN chown -R django:django /app

ENV PATH="/app/.venv/bin:$PATH"

# uv's managed Python interpreters default to $HOME (/root at this point in the
# build), which the non-root `django` user can't read at runtime. Install them
# somewhere world-readable instead.
ENV UV_PYTHON_INSTALL_DIR=/opt/uv/python

# Install Python dependencies
RUN uv sync --no-dev
RUN chmod -R a+rX /opt/uv/python

# Compile Python files
RUN python -m compileall -b . && find . -type f -name "*.py" -delete

USER django

ENTRYPOINT ["/entrypoint"]
