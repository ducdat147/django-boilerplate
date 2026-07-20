# Project Brief: Django Boilerplate

## Overview

A modern Django boilerplate project with best practices, pre-configured packages, and observability tools for rapid development and production-ready applications.

## Core Requirements

- Python 3.13+ with Django 5.2+
- PostgreSQL database with psycopg3
- Redis for caching and Celery broker
- Docker & Docker Compose support
- Modern admin UI with Django Unfold
- RESTful API with DRF and OpenAPI docs

## Goals

1. Provide a production-ready Django starter template
2. Include comprehensive authentication & authorization
3. Integrate observability stack (OpenTelemetry, Grafana, Loki, Tempo)
4. Support asynchronous task processing with Celery
5. Maintain high code quality with automated testing and linting

## Key Features

- Modular settings structure (base, local, production)
- JWT authentication with 2FA support
- Object-level permissions with Django Guardian
- Tailwind CSS v4 for frontend styling
- Comprehensive testing with pytest (target: 80%+ coverage)

## Constraints

- Must maintain compatibility with Docker deployment
- Follow RESTful API best practices
- Use uv for Python package management
- Use pnpm for Node.js package management
