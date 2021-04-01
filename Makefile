SETTINGS ?= pybudgie.config.settings_dev
PORT ?= 9000
MANAGE = ./manage.py
REQUIREMENTS = requirements.txt
REQUIREMENTS_DEV = requirements-dev.txt
ARGS ?=
PO_FILES := $(shell find . -name '*.po')
MO_FILES = $(patsubst %.po,%.mo,$(PO_FILES))

run:
	$(MANAGE) runserver --settings=$(SETTINGS) $(PORT)

migrate:
	$(MANAGE) migrate --settings=$(SETTINGS) $(ARGS)

migrations:
	$(MANAGE) makemigrations --settings=$(SETTINGS) $(ARGS)

superuser:
	$(MANAGE) createsuperuser --settings=$(SETTINGS) $(ARGS)

install-dev: install
	pip install -r $(REQUIREMENTS_DEV) $(ARGS)

install:
	pip install -r $(REQUIREMENTS) $(ARGS)


.generated-locales: 
	$(MANAGE) compilemessages --settings=$(SETTINGS)
	touch .generated-locales

$(MO_FILES): $(PO_FILES)
	$(MANAGE) compilemessages --settings=$(SETTINGS)


.PHONY: generate-locales
generate-locales: $(MO_FILES)

coverage:
	coverage html

run-test:
	coverage run $(MANAGE) test -v2 --noinput --settings=$(SETTINGS) $(ARGS)

test: $(PO_FILES) generate-locales run-test coverage

