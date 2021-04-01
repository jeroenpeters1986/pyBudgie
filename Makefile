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

.PHONY: run
migrate:
	$(MANAGE) migrate --settings=$(SETTINGS) $(ARGS)

.PHONY: run
migrations:
	$(MANAGE) makemigrations --settings=$(SETTINGS) $(ARGS)

.PHONY: run
superuser:
	$(MANAGE) createsuperuser --settings=$(SETTINGS) $(ARGS)

.PHONY: run
install-dev: install
	pip install -r $(REQUIREMENTS_DEV) $(ARGS)

.PHONY: run
install:
	pip install -r $(REQUIREMENTS) $(ARGS)


$(MO_FILES): $(PO_FILES)
	$(MANAGE) compilemessages --settings=$(SETTINGS)


.PHONY: generate-locales
generate-locales: $(MO_FILES)

.PHONY: run
coverage:
	coverage html

.PHONY: run
run-test:
	coverage run $(MANAGE) test -v2 --noinput --settings=$(SETTINGS) $(ARGS)

.PHONY: run
test: $(PO_FILES) generate-locales run-test coverage

