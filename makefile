install:
	pip install --upgrade pip && pip install -r requirements.txt

freeze:
	pip freeze > requirements.txt

update-package:
	pip install -r requirements.txt --upgrade

run:
	python manage.py runserver 0.0.0.0:8000

staticfiles:
	python manage.py collectstatic --noinput

migrate:
	python manage.py makemigrations && python manage.py migrate

migrations:
	python manage.py makemigrations

user:
	python manage.py createsuperuser --username admin --email admin@admin.com

pyc:
	find . -name "*.pyc" -delete && find . -name "*.pyo" -delete && find . -type d -name "__pycache__" -exec rm -r {} +

i:
	pip install $(filter-out $@,$(MAKECMDGOALS)) && pip freeze > requirements.txt

app:
	python manage.py startapp $(filter-out $@,$(MAKECMDGOALS)) ./apps/$(filter-out $@,$(MAKECMDGOALS))

%:
	@:
