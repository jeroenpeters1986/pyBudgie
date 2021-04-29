SETTINGS ?= pybudgie.config.settings_dev
PORT ?= 9000
MANAGE = ./manage.py
REQUIREMENTS = requirements.txt
REQUIREMENTS_DEV = requirements-dev.txt
ARGS ?=
PO_FILES := $(shell find . -name '*.po' |grep -v site-packages)
MO_FILES = $(patsubst %.po,%.mo,$(PO_FILES))

.PHONY: run
run: install install-dev
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

.requirements :requirements.txt
	pip install -r $(REQUIREMENTS) -U $(ARGS)
	touch .requirements

.requirements_dev: requirements-dev.txt
	pip install -r $(REQUIREMENTS) -U $(ARGS)
	touch .requirements_dev


.PHONY: install-dev
install-dev: .requirements_dev

.PHONY: install
install: .requirements


$(MO_FILES): $(PO_FILES)
	$(MANAGE) compilemessages --settings=$(SETTINGS)

.PHONY: generate-locales
generate-locales: $(MO_FILES)

.PHONY: translations
translations: generate-locales

.PHONY: coverage
coverage:
	coverage html

.PHONY: run-test
run-test: install install-dev
	coverage run $(MANAGE) test -v2 --noinput --settings=$(SETTINGS) $(ARGS)

.PHONY: test
test: $(PO_FILES) generate-locales run-test coverage


.PHONY: clean
clean:
	-rm .requirements*
	-rm .coverage
	-rm -rf coverage-reports
	find . -type f -name *.pyc -delete
	find . -type d -name __pycache__ -delete
