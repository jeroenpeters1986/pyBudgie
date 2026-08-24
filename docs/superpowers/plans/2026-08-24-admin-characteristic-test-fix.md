# Admin Characteristic Test Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Use the created `BirdCharacteristic` instance in the admin test while verifying that its name is rendered in the response.

**Architecture:** Keep the change inside the existing `BirdAppAdminTest` test setup and characteristic-options test. Grant the test user the permissions required by the admin inline, then add one response assertion using the already-created model instance; do not change admin behavior.

**Tech Stack:** Python, Django `TestCase`, Django test client.

## Global Constraints

- Modify only `budgie_bird/tests/test_admin.py`.
- Preserve the existing description and JavaScript hook assertions.
- Do not change application code, fixtures, or dependencies.

---

### Task 1: Keep the characteristic inline available to the test user

**Files:**
- Modify: `budgie_bird/tests/test_admin.py:70-88`
- Modify: `budgie_bird/tests/test_admin.py:821-845`
- Test: `budgie_bird/tests/test_admin.py::BirdAppAdminTest::test_admin_bird_characteristic_options_include_descriptions`

**Interfaces:**
- Consumes: The `BirdCharacteristicSelectionInline` permission checks in `budgie_bird/admin.py`.
- Produces: A test user with the characteristic and characteristic-selection permissions needed to render the inline.

- [ ] **Step 1: Include characteristic-related content types in the test permissions**

Extend the existing `ContentType` lookup and `Permission.objects.filter(...)` list
in `setUp` with `BirdCharacteristic` and `BirdCharacteristicSelection`. Do not
alter the admin permission implementation.

- [ ] **Step 2: Add the assertion using the created instance**

Immediately after the response is fetched, add:

```python
        self.assertContains(response, characteristic.name)
```

Keep the existing assertions unchanged:

```python
        self.assertContains(response, "Not applicable")
        self.assertContains(response, "Does not return")
        self.assertContains(response, "characteristic-options")
        self.assertContains(
            response, 'onchange="window.updateCharacteristicGradeLabels(this);"'
        )
```

- [ ] **Step 3: Run the focused test**

Run:

```bash
python manage.py test budgie_bird.tests.test_admin.BirdAppAdminTest.test_admin_bird_characteristic_options_include_descriptions
```

Expected: the test passes, including the new name assertion.

- [ ] **Step 4: Review the diff**

Run:

```bash
git diff -- budgie_bird/tests/test_admin.py
```

Expected: only the test permission setup and the
`assertContains(response, characteristic.name)` line are added; unrelated
existing worktree changes remain untouched.
