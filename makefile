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
	flake8 . --exclude .venv,**/migrations,**/settings/local.py

pre-commit:
	pre-commit run -a

shell:
	python manage.py shell

test:
	coverage run manage.py test

test.report:
	coverage report -m

test.html:
	coverage html

run:
	open http://localhost/
	open http://localhost:3000/
	python manage.py runserver 0.0.0.0:80

celery:
	celery -A configurations.celery worker --pool=threads --loglevel=INFO

message:
	python manage.py makemessages -l en -l vi --no-location --no-wrap

compile: message
	python manage.py compilemessages -l en -l vi

collectstatic:
	${MAKE} css
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

docker.build:
	docker build -t ducdat147/dj.base.project .

docker.login:
	docker login

docker.push: docker.build docker.login
	docker push ducdat147/dj.base.project

deploy:
	docker-compose -f docker-compose.prod.yml up -d
	open http://localhost/
	open http://localhost:3000/

docker.up:
	docker-compose -f docker-compose.local.yml up -d

docker.down.%:
	docker-compose -f docker-compose.$*.yml down -v

clean: css freeze message pre-commit pyc

git.develop:
	git fetch origin
	git checkout develop
	git pull origin develop

git.clean: git.develop
	git for-each-ref --format '%(refname:short)' refs/heads | grep -v "develop" | xargs git branch -D

git.createbranch: git.develop
	git checkout -b $(filter-out $@,$(MAKECMDGOALS))

%:
	@:
