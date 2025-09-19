init:
	mkdir -p logs
	touch logs/query.log
	touch logs/system.log

install:
	pip install --upgrade pip
	pip install -r requirements.txt

freeze:
	pip freeze > requirements.txt

update-package:
	pip install -r requirements.txt --upgrade

shell:
	python manage.py shell

run:
	python manage.py runserver 0.0.0.0:80

celery:
	celery -A configurations.celery worker --pool=threads --loglevel=INFO

message:
	python manage.py makemessages -l en -l vi --no-location --no-wrap

compile:
	python manage.py compilemessages -l en -l vi

staticfiles:
	python manage.py collectstatic --noinput

migrate:
	python manage.py makemigrations
	python manage.py migrate

migrations:
	python manage.py makemigrations

user:
	python manage.py createsuperuser --username admin --email admin@admin.com

pyc:
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -type d -name "__pycache__" -exec rm -r {} +

clear-migrations:
	find ./core/**/migrations -name "0*.py" -delete
	python manage.py makemigrations

css:
	pnpm tailwind:build

i:
	pip install $(filter-out $@,$(MAKECMDGOALS))
	pip freeze > requirements.txt

app:
	mkdir core/$(filter-out $@,$(MAKECMDGOALS))
	python manage.py startapp $(filter-out $@,$(MAKECMDGOALS)) core/$(filter-out $@,$(MAKECMDGOALS))
	mkdir controllers/$(filter-out $@,$(MAKECMDGOALS))
	touch controllers/$(filter-out $@,$(MAKECMDGOALS))/__init__.py
	touch controllers/$(filter-out $@,$(MAKECMDGOALS))/urls.py
	touch controllers/$(filter-out $@,$(MAKECMDGOALS))/views.py
	touch controllers/$(filter-out $@,$(MAKECMDGOALS))/serializers.py

build:
	docker build -t django/service:v1 --file "docker/django/Dockerfile" --no-cache .

compose-up:
	docker-compose --env-file .docker.env up -d

prune:
	docker system prune -a --volumes -f

%:
	@:
