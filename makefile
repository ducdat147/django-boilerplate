install:
	pip install --upgrade pip && pip install -r requirements.txt

freeze:
	pip freeze > requirements.txt

update-package:
	pip install -r requirements.txt --upgrade

run:
	python manage.py runserver 0.0.0.0:8000

pyc:
	find . -name "*.pyc" -delete && find . -name "*.pyo" -delete && find . -type d -name "__pycache__" -exec rm -r {} +
