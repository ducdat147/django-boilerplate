FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=UTC \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    pkg-config \
    gettext \
    && rm -rf /var/lib/apt/lists/*

RUN addgroup --system django \
    && adduser --system --ingroup django django

# Coppy project and install Python dependencies
COPY ./requirements.txt /requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /requirements.txt
RUN pip install uwsgi

COPY ./docker/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint
RUN chown django:django /entrypoint

COPY ./docker/django/start /start-service
RUN sed -i 's/\r$//g' /start-service
RUN chmod +x /start-service
RUN chown django:django /start-service

COPY ./docker/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r$//g' /start-celeryworker
RUN chmod +x /start-celeryworker
RUN chown django:django /start-celeryworker

COPY ./docker/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r$//g' /start-celerybeat
RUN chmod +x /start-celerybeat
RUN chown django:django /start-celerybeat

COPY ./docker/django/celery/flower/start /start-celeryflower
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

# Compile Python files
RUN python -m compileall -b . && find . -type f -name "*.py" -delete

USER django

ENTRYPOINT ["/entrypoint"]
