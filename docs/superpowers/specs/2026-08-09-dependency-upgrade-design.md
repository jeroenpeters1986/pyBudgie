# Dependency upgrade design

## Goal

Update the repository's Python dependencies conservatively while moving Django
from 6.0.2 to 6.1. The upgrade must account for Django 6.1's release notes and
must not introduce unrelated major-version changes.

## Scope

Update `requirements.txt` and `requirements-dev.txt` as follows:

- Upgrade Django to 6.1.
- Upgrade available non-major or patch releases for the pinned dependencies.
- Keep Paramiko 3.x and ReportLab 4.x unchanged for now.
- Replace the beta pin `openpyxl==3.2.0b1` with stable `openpyxl==3.1.5`.

The selected versions are:

Runtime:

```text
asgiref==3.12.1
certifi==2026.7.22
Django==6.1
django-admin-interface==0.32.0
django-colorfield==0.14.0
django-flat-responsive==2.0
django-flat-theme==1.1.4
django-storages==1.14.6
et-xmlfile==2.0.0
mysqlclient==2.2.7; platform_system != "Darwin"
openpyxl==3.1.5
paramiko==3.5.1
pillow==12.3.0
python-dotenv==1.2.2
reportlab==4.4.4
pytz==2026.3.post1
six==1.17.0
```

Development:

```text
black==26.5.1
coverage==7.15.4
pycodestyle==2.14.0
pydocstyle==6.3.0
pyflakes==3.4.0
pylama==8.4.1
pylint==4.0.6
pytest==9.1.1
setuptools==80.9.0
```

Compatibility note: pylama==8.4.1 imports pkg_resources; setuptools 84.0.0 no longer provides pkg_resources, while setuptools 80.9.0 restores it. We intentionally pin setuptools==80.9.0 so pylama runs (and consequently surfaces the pre-existing W0612 at budgie_bird/tests/test_admin.py:822). This is a conservative, documented compatibility tradeoff.

## Django 6.1 compatibility assessment

The application code does not use the removed Django APIs identified in the
6.1 release notes. No changes are planned for model `on_delete` behavior,
email mailers, JSON null handling, `select_related()`, `values_list()`, or
custom database backends.

Production uses MariaDB 10.11, which satisfies Django 6.1's minimum supported
MariaDB version. Local tests use SQLite; that must be at least SQLite 3.37.
The existing Python environment is Python 3.14, which Django 6.1 supports.

The existing `STORAGES` configuration remains compatible. The legacy
`DEFAULT_FILE_STORAGE` setting in the development/live configuration is not
changed as part of this upgrade because it is unrelated to a Django 6.1
release-note incompatibility and the storage behavior must remain unchanged.

## Validation

After updating the pins:

1. Run Django system checks with the test settings.
2. Run migrations in check mode.
3. Run the repository's existing test target.
4. Run the configured linting checks if they are part of the existing project
   workflow.

If a dependency or integration fails, make only the smallest compatibility
adjustment needed and document the reason in the implementation change.
