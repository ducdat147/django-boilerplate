export UV_ENV_FILE := .env.host

init:
	mkdir -p logs

install.dev: update-package
	uv sync --locked
	uv run pre-commit install

install: update-package
	uv sync --no-dev
	uv run pre-commit install

update-package:
	uv lock --upgrade
	pnpm install
	pnpm update --latest

lint:
	uv run ruff check --select I --fix .
	uv run ruff format

pre-commit:
	uv run pre-commit run -a

shell:
	uv run python manage.py shell

seed_data:
	uv run python manage.py seed_data

# Testing commands
test:
	uv run pytest

test.unit:
	uv run pytest -m unit

test.integration:
	uv run pytest -m integration

test.fast:
	uv run pytest -m "not slow"

test.coverage:
	uv run pytest --cov --cov-report=html --cov-report=term

test.watch:
	uv run pytest-watch

test.parallel:
	uv run pytest -n auto

test.verbose:
	uv run pytest -vv

test.failed:
	uv run pytest --lf

test.file:
	uv run pytest $(filter-out $@,$(MAKECMDGOALS))

test.django:
	uv run coverage run manage.py test

test.django.report:
	uv run coverage report -m

test.django.html:
	uv run coverage html

run:
	uv run python manage.py runserver 0.0.0.0:80

celery:
	uv run celery -A configurations.celery worker --pool=threads --loglevel=INFO

message:
	uv run python manage.py makemessages -l en -l vi --no-location --no-wrap

compile: message
	uv run python manage.py compilemessages -l en -l vi

collectstatic:
	${MAKE} css
	uv run python manage.py collectstatic --noinput

migrations:
	uv run python manage.py makemigrations

migrate: migrations
	uv run python manage.py migrate

user:
	${MAKE} migrate
	uv run python manage.py createsuperuser --username admin --email admin@admin.com

pyc:
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -type d -name "__pycache__" -exec rm -r {} +

clear-migrations:
	find ./core/**/migrations -name "0*.py" -delete
	${MAKE} migrations

css:
	pnpm tailwind:build

i:
	uv add $(filter-out $@,$(MAKECMDGOALS))

i.dev:
	uv add --dev $(filter-out $@,$(MAKECMDGOALS))

r:
	uv remove $(filter-out $@,$(MAKECMDGOALS))

r.dev:
	uv remove --dev $(filter-out $@,$(MAKECMDGOALS))

app:
	if test ! -d core/$(filter-out $@,$(MAKECMDGOALS)); then mkdir core/$(filter-out $@,$(MAKECMDGOALS)); fi
	if test ! -d core/$(filter-out $@,$(MAKECMDGOALS))/migrations; then mkdir core/$(filter-out $@,$(MAKECMDGOALS))/migrations; fi
	touch \
	core/$(filter-out $@,$(MAKECMDGOALS))/__init__.py \
	core/$(filter-out $@,$(MAKECMDGOALS))/migrations/__init__.py \
	core/$(filter-out $@,$(MAKECMDGOALS))/apps.py \
	core/$(filter-out $@,$(MAKECMDGOALS))/admin.py \
	core/$(filter-out $@,$(MAKECMDGOALS))/enums.py \
	core/$(filter-out $@,$(MAKECMDGOALS))/models.py \
	core/$(filter-out $@,$(MAKECMDGOALS))/urls.py \
	core/$(filter-out $@,$(MAKECMDGOALS))/views.py \
	core/$(filter-out $@,$(MAKECMDGOALS))/serializers.py
	echo "from django.apps import AppConfig as DjangoAppConfig\nfrom django.conf import settings\n\n\nclass AppConfig(DjangoAppConfig):\n    default_auto_field = settings.DEFAULT_AUTO_FIELD\n    name = \"core.$(filter-out $@,$(MAKECMDGOALS))\"" > core/$(filter-out $@,$(MAKECMDGOALS))/apps.py

prune:
	docker system prune -a --volumes -f

docker.build:
	docker build -t ducdat147/dj.base.project .

docker.login:
	docker login

docker.push:
	${MAKE} docker.build
	${MAKE} docker.login
	docker push ducdat147/dj.base.project

docker.devops.up:
	docker-compose -f docker-compose.devops.yml up -d

docker.up:
	${MAKE} docker.devops.up
	docker-compose -f docker-compose.local.yml up -d

docker.webserver.up:
	docker-compose -f docker-compose.webserver.yml up -d

docker.down.%:
	docker-compose -f docker-compose.$*.yml down -v

deploy:
	${MAKE} docker.devops.up
	docker-compose -f docker-compose.prod.yml up -d
	${MAKE} docker.webserver.up
	open http://localhost/
	open http://localhost:3000/

clean: css message pyc pre-commit

git.develop:
	git fetch origin
	git checkout develop
	git pull origin develop

git.clean:
	${MAKE} git.develop
	git for-each-ref --format '%(refname:short)' refs/heads | grep -v "develop" | xargs git branch -D

git.createbranch:
	${MAKE} git.develop
	git checkout -b feature/$(filter-out $@,$(MAKECMDGOALS))

%:
	@:
