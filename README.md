# pyBudgie
Keep track of your budgies

[![Python support](https://img.shields.io/badge/python-3.6+-blue.svg)](https://devguide.python.org/#status-of-python-branches)
[![Django support](https://img.shields.io/badge/django-3.1+-brightgreen.svg)](https://djangoproject.com)
[![Tests status](https://github.com/jeroenpeters1986/pyBudgie/actions/workflows/ci.yml/badge.svg)](https://github.com/jeroenpeters1986/pyBudgie/actions)
[![Coverage](https://jeroenpeters1986.github.io/pyBudgie/badges/coverage.svg)](https://github.com/jeroenpeters1986/pyBudgie/actions)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

## Setup 
### Custom User Auth
settings.py
```
AUTH_USER_MODEL = 'budgie_account.BudgieUser'
```

## Useful resources
 * https://djangowaves.com/tutorial/multiple-languages-in-Django/
 * https://docs.djangoproject.com/en/3.1/topics/testing/tools/
 * https://github.com/ripienaar/free-for-dev (for hosting, later on)
 * https://github.com/fabiocaccamo/django-admin-interface/
 * https://help.alwaysdata.com/en/languages/python/django/
 * https://books.agiliq.com/projects/django-admin-cookbook/en/latest/
 * https://stackoverflow.com/a/54531546 (url list for admin debugging)
 * https://docs.djangoproject.com/en/3.1/ref/databases/#connecting-to-the-database

## System requirements
 * Django 3.1 or higher
 * (min) Python 3.6

### Author todo:
CSS-addition:
```css
select[multiple] {
   min-width: 20em;
}
```