init:
	mkdir -p logs

install:
	pip install --upgrade pip
	pip install -r requirements.txt
	pre-commit install

freeze:
	pip freeze > requirements.txt

update-package:
	pip install -r requirements.txt --upgrade

lint:
	flake8 . --exclude .venv,**/migrations

pre-commit:
	pre-commit run -a

shell:
	python manage.py shell

run:
	python manage.py runserver 0.0.0.0:80

celery:
	celery -A configurations.celery worker --pool=threads --loglevel=INFO

message:
	python manage.py makemessages -l en -l vi --no-location --no-wrap

compile: message
	python manage.py compilemessages -l en -l vi

staticfiles:
	python manage.py collectstatic --noinput

migrations:
	python manage.py makemigrations

migrate: migrations
	python manage.py migrate

user:
	python manage.py createsuperuser --username admin --email admin@admin.com

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

prune:
	docker system prune -a --volumes -f

build:
	# docker rm -f server celery_worker celery_beat celery_flower
	# docker rmi server:latest
	docker build -t server:latest --file "docker/django/Dockerfile" --no-cache .

deploy: build
	docker-compose -f docker-compose.prod.yml up -d

docker-up:
	docker-compose -f docker-compose.local.yml up -d

docker-down.%:
	docker-compose -f docker-compose.$*.yml down -v
	${MAKE} prune

clean: css freeze lint message pyc pre-commit

%:
	@:
