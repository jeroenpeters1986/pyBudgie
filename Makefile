SETTINGS ?= pybudgie.config.settings_dev
SETTINGS_TEST ?= pybudgie.config.settings_ci
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

install:
	pip install -r $(REQUIREMENTS) $(ARGS)

coverage:
	coverage html

run-test:
	coverage run $(MANAGE) test -v2 --noinput --settings=$(SETTINGS_TEST) $(ARGS)

test: run-test coverage

