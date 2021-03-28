SETTINGS ?= pybudgie.config.settings_dev
PORT ?= 9000
MANAGE = ./manage.py
REQUIREMENTS = requirements.txt
ARGS ?=

run:
	$(MANAGE) runserver --settings=$(SETTINGS) $(PORT)

migrate:
	$(MANAGE) migrate --settings=$(SETTINGS) $(ARGS)

migrations:
	$(MANAGE) makemigrations --settings=$(SETTINGS) $(ARGS)

superuser:
	$(MANAGE) createsuperuser --settings=$(SETTINGS) $(ARGS)

install:
	pip install -r $(REQUIREMENTS) $(ARGS)

generate-locales:
	$(MANAGE) compilemessages --settings=$(SETTINGS)

coverage:
	coverage html

run-test:
	coverage run $(MANAGE) test -v2 --noinput --settings=$(SETTINGS) $(ARGS)

test: generate-locales run-test coverage

