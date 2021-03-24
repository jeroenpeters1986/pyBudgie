SETTINGS ?= pybudgie.config.settings_dev
PORT ?= 9000
MANAGE = ./manage.py
REQUIREMENTS = pyBudgie/requirements.txt
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
	coverage run $(MANAGE) test -v2 --noinput --settings=$(SETTINGS) $(ARGS)

test: run-test coverage

