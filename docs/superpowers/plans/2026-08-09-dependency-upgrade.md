# Conservative Dependency Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the repository to Django 6.1 and current compatible non-major dependency versions without changing application behavior.

**Architecture:** Keep dependency policy in the two existing requirements files. Do not change application code unless validation identifies a concrete Django 6.1 incompatibility. Validate in an isolated virtual environment with the existing Django checks, migration check, tests, and lint commands.

**Tech Stack:** Python 3.14, Django 6.1, SQLite test database, MariaDB 10.11 production database, pip, Make, Django test runner, pytest, coverage, and pylama.

## Global Constraints

- Production MariaDB is 10.11, satisfying Django 6.1's MariaDB minimum.
- Django 6.1 supports the repository's Python 3.14 runtime.
- Local SQLite must be at least SQLite 3.37.
- Keep Paramiko 3.x and ReportLab 4.x unchanged.
- Replace beta `openpyxl==3.2.0b1` with stable `openpyxl==3.1.5`.
- Do not change storage behavior or introduce unrelated application refactoring.
- Preserve the user's existing modification to `pybudgie/locale/nl/LC_MESSAGES/django.po`.

---

### Task 1: Update dependency pins

**Files:**
- Modify: `requirements.txt`
- Modify: `requirements-dev.txt`

**Interfaces:**
- Consumes: The current exact-version dependency pins.
- Produces: Exact pins matching the approved dependency upgrade specification.

- [ ] **Step 1: Replace runtime pins**

Update only the following lines in `requirements.txt`:

```text
asgiref==3.12.1
certifi==2026.7.22
Django==6.1
django-admin-interface==0.32.0
openpyxl==3.1.5
pillow==12.3.0
pytz==2026.3.post1
```

Leave all other runtime lines unchanged, including `paramiko==3.5.1` and
`reportlab==4.4.4`.

- [ ] **Step 2: Replace development pins**

Update only the following lines in `requirements-dev.txt`:

```text
black==26.5.1
coverage==7.15.4
pylint==4.0.6
pytest==9.1.1
setuptools==84.0.0
```

Leave `pycodestyle`, `pydocstyle`, `pyflakes`, and `pylama` unchanged because
their current pins already match the latest available versions.

- [ ] **Step 3: Review the dependency diff**

Run:

```bash
git diff -- requirements.txt requirements-dev.txt
```

Expected: only the explicitly listed pins change; no line is added for a
major Paramiko or ReportLab upgrade.

- [ ] **Step 4: Commit the pin changes**

```bash
git add requirements.txt requirements-dev.txt
git commit -m "deps: upgrade Django and compatible dependencies" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

### Task 2: Resolve dependencies in isolation

**Files:**
- No repository files modified.

**Interfaces:**
- Consumes: `requirements.txt` and `requirements-dev.txt` from Task 1.
- Produces: An isolated environment containing the exact requested versions.

- [ ] **Step 1: Create a temporary virtual environment outside the repository**

Run:

```bash
python3 -m venv /tmp/pybudgie-dependency-upgrade
/tmp/pybudgie-dependency-upgrade/bin/python -m pip install --upgrade pip
```

Expected: the virtual environment is created without altering the repository
or the system Python installation.

- [ ] **Step 2: Install runtime and development requirements**

Run:

```bash
/tmp/pybudgie-dependency-upgrade/bin/pip install -r requirements.txt -r requirements-dev.txt
```

Expected: pip resolves Django 6.1 and all exact pins. On macOS,
`mysqlclient` is skipped by its existing platform marker.

- [ ] **Step 3: Confirm the important versions**

Run:

```bash
/tmp/pybudgie-dependency-upgrade/bin/python -c "import django, openpyxl; print(django.get_version()); print(openpyxl.__version__)"
```

Expected output contains:

```text
6.1
3.1.5
```

### Task 3: Validate Django 6.1 behavior

**Files:**
- No repository files modified unless a concrete validation failure requires a
  narrowly scoped compatibility fix.

**Interfaces:**
- Consumes: The isolated environment from Task 2 and
  `pybudgie.config.settings_test`.
- Produces: Evidence that checks, migrations, and tests remain compatible with
  Django 6.1.

- [ ] **Step 1: Run Django system checks**

Run:

```bash
/tmp/pybudgie-dependency-upgrade/bin/python manage.py check --settings=pybudgie.config.settings_test
```

Expected: the command exits successfully. The existing intentional
`security.W019` suppression remains the only suppressed security check.

- [ ] **Step 2: Check for unapplied model migrations**

Run:

```bash
/tmp/pybudgie-dependency-upgrade/bin/python manage.py makemigrations --check --dry-run --settings=pybudgie.config.settings_test
```

Expected: no model changes are reported.

- [ ] **Step 3: Run the existing test suite**

Run:

```bash
/tmp/pybudgie-dependency-upgrade/bin/python manage.py test --noinput --settings=pybudgie.config.settings_test
```

Expected: all existing tests pass. If a failure is caused by a Django 6.1
removed or deprecated API, update only the affected code path and add a
focused regression test in the existing test module.

- [ ] **Step 4: Run the existing lint command**

Run:

```bash
/tmp/pybudgie-dependency-upgrade/bin/pylama
```

Expected: the command completes with no new issues caused by the dependency
upgrade.

- [ ] **Step 5: Remove the temporary environment**

Run:

```bash
rm -rf /tmp/pybudgie-dependency-upgrade
```

Expected: no temporary dependency environment remains.

- [ ] **Step 6: Record the final repository state**

Run:

```bash
git status --short
git log -2 --oneline
```

Expected: only intentional dependency or compatibility changes are present;
the pre-existing locale modification remains untouched.
