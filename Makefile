SETTINGS ?= pybudgie.config.settings_dev
PORT ?= 9000
MANAGE = ./manage.py
REQUIREMENTS = requirements.txt
REQUIREMENTS_DEV = requirements-dev.txt
ARGS ?=
PO_FILES := $(shell find . -name '*.po')
MO_FILES = $(patsubst %.po,%.mo,$(PO_FILES))

.PHONY: run
run:
	$(MANAGE) runserver --settings=$(SETTINGS) $(PORT)

.PHONY: migrate
migrate:
	$(MANAGE) migrate --settings=$(SETTINGS) $(ARGS)

.PHONY: migrations
migrations:
	$(MANAGE) makemigrations --settings=$(SETTINGS) $(ARGS)

.PHONY: superuser
superuser:
	$(MANAGE) createsuperuser --settings=$(SETTINGS) $(ARGS)

.PHONY: install-dev
install-dev: install
	pip install -r $(REQUIREMENTS_DEV) $(ARGS)

.PHONY: install
install:
	pip install -r $(REQUIREMENTS) $(ARGS)


$(MO_FILES): $(PO_FILES)
	$(MANAGE) compilemessages --settings=$(SETTINGS)

.PHONY: generate-locales
generate-locales: $(MO_FILES)

.PHONY: coverage
coverage:
	coverage html

.PHONY: run-test
run-test:
	coverage run $(MANAGE) test -v2 --noinput --settings=$(SETTINGS) $(ARGS)

.PHONY: test
test: $(PO_FILES) generate-locales run-test coverage

