# pyBudgie
Keep track of your budgies

## Shiny badges
Hopefully they're all nice and green

[![Python](https://img.shields.io/badge/python-3.7|3.8|3.9-brightgreen.svg)](https://devguide.python.org/#status-of-python-branches)
[![Python](https://img.shields.io/badge/django-3.1|3.2-brightgreen.svg)](https://djangoproject.com)
[![Github Actions](https://github.com/jeroenpeters1986/pyBudgie/actions/workflows/ci.yml/badge.svg)](https://github.com/jeroenpeters1986/pyBudgie/actions)

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