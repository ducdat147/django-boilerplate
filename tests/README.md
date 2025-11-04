# Testing Documentation

> **Comprehensive Testing Guide for Django Boilerplate Project**
>
> Last Updated: November 3, 2025
> Testing Framework: pytest 8.4.2
> Coverage: 52.20% (targeting 80%+)

---

## 📖 Table of Contents

1. [Quick Start](#-quick-start)
2. [Overview](#-overview)
3. [Test Organization](#-test-organization)
4. [Running Tests](#-running-tests)
5. [Writing Tests](#-writing-tests)
6. [Testing Standards](#-testing-standards)
7. [Best Practices](#-best-practices)
8. [Troubleshooting](#-troubleshooting)
9. [Migration Guide](#-migration-guide)
10. [Analysis & Metrics](#-analysis--metrics)

---

## 🚀 Quick Start

### Installation

```bash
# Install all testing dependencies
make i.dev pytest pytest-django pytest-cov pytest-mock pytest-xdist

# Or using uv directly
uv add --dev pytest pytest-django pytest-cov pytest-mock pytest-xdist
```

### Run Tests

```bash
# Run all tests with coverage
make test

# Run specific test types
make test.unit         # Unit tests only (fast, ~1 second)
make test.integration  # Integration tests only
make test.fast         # Skip slow tests
make test.coverage     # Generate HTML coverage report

# Run tests in parallel (faster)
make test.parallel
```

### Check Coverage

```bash
# Generate and open HTML coverage report
make test.coverage
open htmlcov/index.html
```

### Current Status

- ✅ **12 passing tests** (5 unit + 7 integration) with **100% pass rate**
- ✅ **52.20% code coverage** (baseline established, **targeting 80%+**)
- ✅ **~2.6 second execution time** for full test suite
- ✅ **Zero test failures** - all tests green
- ✅ **Modern pytest framework** with fixtures and parallel execution

---

## 📋 Overview

This directory contains all test files for the Django boilerplate project using a **modern pytest-based testing framework**.

### Recent Migration

Successfully migrated from Django's traditional test framework to pytest (October 2025), providing:

- Better fixtures system
- Clearer test organization
- Faster execution (~50% improvement)
- Better IDE integration
- More detailed failure output

### Technology Stack

**Core Testing Framework:**

- **pytest 8.4.2** - Modern Python testing framework with powerful features
- **pytest-django 4.11.1** - Django integration with database fixtures
- **pytest-cov 7.0.0** - Code coverage reporting
- **pytest-mock 3.15.1** - Mocking and patching capabilities
- **pytest-xdist 3.8.0** - Parallel test execution

**Configuration Files:**

- `pytest.ini` - Pytest configuration with markers and coverage settings
- `.coveragerc` - Coverage configuration (45% minimum, targeting 80%)
- `tests/conftest.py` - Shared fixtures for all tests
- `tests/mixins.py` - Reusable test mixins and utilities

---

## 📁 Test Organization

### Directory Structure

```
tests/
├── README.md                     # This comprehensive documentation
├── conftest.py                   # Pytest fixtures (6 fixtures defined)
│                                 # - api_client, user, verified_user
│                                 # - admin_user, authenticated_client, admin_client
│
├── mixins.py                     # Reusable test utilities
│                                 # - APITestMixin (response assertions)
│                                 # - CRUDTestMixin (CRUD operation tests)
│                                 # - PermissionTestMixin (auth checks)
│                                 # - PerformanceTestMixin (query optimization)
│
├── unit/                         # Unit tests (70% of suite)
│   ├── models/                   # Model tests (validation, methods)
│   ├── views/                    # View/API endpoint tests
│   │   └── test_user_views.py   # ✅ 5 tests: profile GET/PATCH, password reset
│   └── serializers/              # Serializer validation tests
│
├── integration/                  # Integration tests (25% of suite)
│   └── test_auth_flow.py        # ✅ 7 tests: complete auth workflows
│
├── performance/                  # Performance tests (planned)
│   └── test_api_performance.py  # N+1 queries, response time
│
├── e2e/                          # End-to-end tests (planned)
│   └── test_user_journey.py     # Complete user flows
│
└── test_case/                    # Legacy JSON-based tests (deprecated)
    ├── __init__.py               # ⚠️ Deprecated - migrate to pytest
    ├── auth.json                 # ⚠️ Deprecated
    └── user.json                 # ⚠️ Deprecated
```

### Testing Pyramid

Tests follow the **testing pyramid** pattern:

```
       /\
      /  \      E2E Tests (5%)
     /----\     - Full user journeys (planned)
    /      \
   /--------\   Integration Tests (25%)
  /          \  - Authentication flows
 /------------\ - User management workflows
/______________\
                Unit Tests (70%)
                - Models, serializers, views
                - Fast, isolated, focused
```

**Benefits:**

- **70% Unit Tests**: Fast feedback, easy debugging
- **25% Integration Tests**: Verify component interactions
- **5% E2E Tests**: Verify complete user workflows

---

## 🏃 Running Tests

### Basic Commands

```bash
# Run all tests with coverage report
make test

# Run specific test types
make test.unit              # Unit tests only (fast, ~1 second)
make test.integration       # Integration tests only
make test.fast              # Skip slow tests (@pytest.mark.slow)
```

### Coverage & Reporting

```bash
# Generate detailed HTML coverage report
make test.coverage
# Opens htmlcov/index.html automatically with:
# - Line-by-line coverage
# - Branch coverage
# - Missing lines highlighted

# View coverage in terminal
pytest --cov --cov-report=term-missing
```

### Performance & Debugging

```bash
# Run tests in parallel (4x faster)
make test.parallel

# Verbose output with detailed test information
make test.verbose

# Re-run only previously failed tests
make test.failed

# Run tests in a specific file
make test.file tests/unit/views/test_user_views.py

# Run specific test class or method
pytest tests/unit/views/test_user_views.py::TestUserProfileView
pytest tests/unit/views/test_user_views.py::TestUserProfileView::test_get_profile_authenticated
```

### Advanced Options

```bash
# Run with live output (see prints)
pytest -s

# Stop on first failure
pytest -x

# Show local variables in tracebacks
pytest -l

# Run tests matching a keyword
pytest -k "profile"

# Show slowest 10 tests
pytest --durations=10

# Run with specific markers
pytest -m unit              # Run only unit tests
pytest -m integration       # Run only integration tests
pytest -m "not slow"        # Skip slow tests
```

### Legacy Commands (Deprecated)

```bash
# ⚠️ These are deprecated - use pytest instead
make test.django           # Old Django test runner
make test.django.report    # Old coverage report
make test.django.html      # Old HTML coverage
```

---

## ✍️ Writing Tests

### Available Fixtures

Six pre-configured fixtures available in all tests (defined in `tests/conftest.py`):

| Fixture                | Type      | Description                                                          | Example Usage                          |
| ---------------------- | --------- | -------------------------------------------------------------------- | -------------------------------------- |
| `api_client`           | APIClient | Unauthenticated DRF client                                           | Testing public endpoints, registration |
| `user`                 | User      | Basic test user<br/>`username: testuser`<br/>`password: testpass123` | Generic user tests                     |
| `verified_user`        | User      | User with profile created<br/>Email & phone verified                 | Profile-dependent tests                |
| `admin_user`           | User      | Superuser with admin privileges                                      | Admin panel, staff functionality       |
| `authenticated_client` | APIClient | JWT-authenticated client<br/>(uses `verified_user`)                  | Protected API endpoints                |
| `admin_client`         | APIClient | Admin-authenticated client                                           | Admin-only endpoints                   |

### Test Markers

Use pytest markers to categorize tests:

```python
@pytest.mark.unit          # Fast, isolated unit tests
@pytest.mark.integration   # Multi-component integration tests
@pytest.mark.slow          # Tests taking >1 second
@pytest.mark.e2e          # End-to-end tests (planned)
```

### Example 1: Unit Test

```python
# tests/unit/views/test_user_views.py
import pytest
from rest_framework import status
from django.urls import reverse

@pytest.mark.unit
class TestUserProfileView:
    """Test user profile view endpoints."""

    @pytest.fixture
    def url(self):
        """Profile endpoint URL."""
        return reverse("user:my_profile")

    def test_get_profile_authenticated(self, authenticated_client, verified_user, url):
        """Test getting profile with authentication."""
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == verified_user.username
        assert "password" not in response.data

    def test_get_profile_unauthenticated(self, api_client, url):
        """Test getting profile without authentication returns 401."""
        response = api_client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile(self, authenticated_client, verified_user, url):
        """Test updating user profile."""
        data = {
            "first_name": "Updated",
            "last_name": "Name"
        }
        response = authenticated_client.patch(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "Updated"

        # Verify database was updated
        verified_user.refresh_from_db()
        assert verified_user.first_name == "Updated"
```

### Example 2: Integration Test

```python
# tests/integration/test_auth_flow.py
import pytest
from rest_framework import status
from django.urls import reverse

@pytest.mark.integration
class TestAuthenticationFlow:
    """Test complete authentication flow."""

    def test_complete_registration_login_flow(self, api_client, db):
        """Test user registration and login workflow."""
        # Step 1: Register a new user
        register_url = reverse("auth:register")
        register_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "phone": "+84369000001",
        }
        register_response = api_client.post(register_url, register_data, format="json")

        assert register_response.status_code == status.HTTP_201_CREATED
        assert "access" in register_response.data
        assert "refresh" in register_response.data

        # Step 2: Login with created credentials
        login_url = reverse("auth:token_obtain_pair")
        login_data = {"username": "newuser", "password": "SecurePass123!"}
        login_response = api_client.post(login_url, login_data, format="json")

        assert login_response.status_code == status.HTTP_200_OK
        assert "access" in login_response.data

        # Step 3: Access protected resource with token
        access_token = login_response.data["access"]
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        profile_url = reverse("user:my_profile")
        profile_response = api_client.get(profile_url)

        assert profile_response.status_code == status.HTTP_200_OK
        assert profile_response.data["username"] == "newuser"
```

### Example 3: Parametrized Tests

```python
@pytest.mark.parametrize("email,is_valid", [
    ("test@example.com", True),
    ("invalid-email", False),
    ("@example.com", False),
    ("test@", False),
    ("", False),
])
def test_email_validation(email, is_valid):
    """Test email validation with multiple inputs."""
    result = validate_email(email)
    assert result == is_valid
```

### Example 4: Using Test Mixins

```python
from tests.mixins import APITestMixin, CRUDTestMixin

class TestUserAPI(APITestMixin, CRUDTestMixin):
    """Test User API with reusable mixins."""

    def test_create_user(self, api_client):
        """Test user creation."""
        response = self.create_instance(api_client, "/api/users/", {
            "username": "testuser",
            "email": "test@example.com"
        })
        self.assert_created(response)
        self.assert_has_keys(response.data, ["id", "username", "email"])
```

### Example 5: Model Tests

```python
# tests/unit/models/test_user_model.py
import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

@pytest.mark.unit
class TestUserModel:
    """Test User model."""

    def test_create_user_with_email(self, db):
        """Test creating a user with email is successful."""
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.check_password("testpass123")
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_user_string_representation(self, user):
        """Test the user string representation."""
        assert str(user) == user.username

    @pytest.mark.parametrize("username,expected", [
        ("user1", True),
        ("", False),
        ("a" * 151, False),  # Too long
    ])
    def test_username_validation(self, db, username, expected):
        """Test username validation."""
        try:
            user = User(username=username, email="test@test.com")
            user.full_clean()
            result = True
        except ValidationError:
            result = False

        assert result == expected
```

---

## 📏 Testing Standards

### The AAA Pattern

All tests should follow the **Arrange-Act-Assert** pattern:

```python
def test_something(authenticated_client):
    # Arrange - Setup data and preconditions
    data = {'name': 'Test'}
    url = reverse('api:endpoint')

    # Act - Perform the action being tested
    response = authenticated_client.post(url, data, format="json")

    # Assert - Check the results
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['name'] == 'Test'
```

### Test Naming Convention

Use descriptive names that explain:

1. What is being tested
2. Under what conditions
3. What is the expected result

```python
# ❌ Bad - Unclear what's being tested
def test_user():
    ...

def test_profile():
    ...

# ✅ Good - Clear and descriptive
def test_create_user_with_valid_data_succeeds():
    ...

def test_get_profile_without_authentication_returns_401():
    ...

def test_update_profile_with_invalid_email_returns_400():
    ...
```

### Test Independence

Each test should be completely independent:

```python
# ❌ Bad - Tests depend on execution order
def test_create_user(self):
    self.user_id = create_user()  # Shared state

def test_update_user(self):
    update_user(self.user_id)  # Depends on previous test

# ✅ Good - Each test is independent
def test_create_user(api_client, db):
    response = api_client.post(url, data, format="json")
    assert response.status_code == 201

def test_update_user(api_client, user):  # Uses fixture
    response = api_client.patch(url, data, format="json")
    assert response.status_code == 200
```

### Fixture Usage

Prefer fixtures over setUp/tearDown:

```python
# ❌ Bad - Using setUp/tearDown
class TestUser(TestCase):
    def setUp(self):
        self.user = User.objects.create(...)

    def tearDown(self):
        self.user.delete()

# ✅ Good - Using fixtures
@pytest.fixture
def user(db):
    return User.objects.create(...)

def test_something(user):
    assert user.username == "testuser"
```

### Mocking External Services

Always mock external dependencies:

```python
# ❌ Bad - Calling real email service
def test_send_email():
    send_email("test@example.com", "Subject", "Body")
    # Slow, unreliable, side effects

# ✅ Good - Mocking email service
def test_send_email(mocker):
    mock_send = mocker.patch('django.core.mail.send_mail')

    send_email("test@example.com", "Subject", "Body")

    mock_send.assert_called_once_with(
        "Subject",
        "Body",
        "from@example.com",
        ["test@example.com"]
    )
```

### Coverage Targets

| Test Type             | Coverage Target      | Priority |
| --------------------- | -------------------- | -------- |
| **Unit Tests**        | 90%+                 | High     |
| **Integration Tests** | Cover critical flows | High     |
| **Overall Project**   | 80%+                 | Medium   |
| **Models**            | 95%+                 | High     |
| **Views/APIs**        | 85%+                 | High     |
| **Utilities**         | 90%+                 | Medium   |

### Test Organization Standards

```
tests/
├── unit/                    # 70% of total tests
│   ├── models/              # Model-specific tests
│   ├── serializers/         # Serializer validation
│   ├── views/               # API endpoint tests
│   └── utils/               # Utility function tests
│
├── integration/             # 25% of total tests
│   ├── test_auth_flow.py    # Authentication workflows
│   └── test_user_flow.py    # User management workflows
│
└── e2e/                     # 5% of total tests
    └── test_complete_journey.py  # Full user journeys
```

---

## ✅ Best Practices

### DO ✅

1. **Write descriptive test names**

   ```python
   def test_user_registration_with_valid_data_creates_user_and_returns_tokens()
   ```

2. **Follow AAA pattern** (Arrange-Act-Assert)

   ```python
   def test_something():
       # Arrange
       data = prepare_data()
       # Act
       result = perform_action(data)
       # Assert
       assert result == expected
   ```

3. **Use specific fixtures**

   ```python
   def test_profile(authenticated_client, verified_user):  # Clear dependencies
   ```

4. **Add format="json" to POST/PUT/PATCH**

   ```python
   response = api_client.post(url, data, format="json")
   ```

5. **Use pytest markers**

   ```python
   @pytest.mark.unit
   @pytest.mark.integration
   @pytest.mark.slow
   ```

6. **Test both success and failure**

   ```python
   def test_login_with_valid_credentials_succeeds()
   def test_login_with_invalid_credentials_fails()
   ```

7. **Use parametrize for variations**

   ```python
   @pytest.mark.parametrize("input,expected", [...])
   ```

8. **Mock external services**

   ```python
   @pytest.fixture
   def mock_email(mocker):
       return mocker.patch('django.core.mail.send_mail')
   ```

9. **Keep tests fast**

   - Use `--reuse-db` flag
   - Mock slow operations
   - Run in parallel

10. **Write docstrings**
    ```python
    def test_something():
        """Test that user can login with valid credentials."""
    ```

### DON'T ❌

1. **Mix authentication states**

   ```python
   # ❌ Bad
   def test_profile(api_client, user):
       # Unclear if authenticated or not
   ```

2. **Forget format="json"**

   ```python
   # ❌ Bad - causes 415 Unsupported Media Type
   response = api_client.post(url, data)

   # ✅ Good
   response = api_client.post(url, data, format="json")
   ```

3. **Skip test markers**

   ```python
   # ❌ Bad - can't filter tests
   def test_something():

   # ✅ Good
   @pytest.mark.unit
   def test_something():
   ```

4. **Test implementation details**

   ```python
   # ❌ Bad - testing internals
   assert view._internal_method() == something

   # ✅ Good - testing behavior
   assert response.status_code == 200
   ```

5. **Share state between tests**

   ```python
   # ❌ Bad
   class TestUser:
       user = None  # Shared across tests

   # ✅ Good
   @pytest.fixture
   def user(db):
       return User.objects.create(...)
   ```

6. **Write vague test names**

   ```python
   # ❌ Bad
   def test_profile()
   def test_user()

   # ✅ Good
   def test_get_profile_authenticated_returns_user_data()
   ```

7. **Ignore edge cases**

   ```python
   # Test null, empty, max length, special characters, etc.
   ```

8. **Skip assertions**

   ```python
   # ❌ Bad - no verification
   response = api_client.get(url)

   # ✅ Good
   response = api_client.get(url)
   assert response.status_code == 200
   assert "username" in response.data
   ```

---

## 🐛 Troubleshooting

### Common Issues & Solutions

#### 1. 415 Unsupported Media Type

**Symptom:**

```python
AssertionError: 415 != 201
```

**Cause:** Missing `format="json"` in POST/PUT/PATCH requests

**Fix:**

```python
# ❌ Bad
response = api_client.post(url, data)

# ✅ Good
response = api_client.post(url, data, format="json")
```

#### 2. 401 Unauthorized on Profile Endpoints

**Symptom:**

```python
AssertionError: 401 != 200
```

**Cause:** Using `user` fixture instead of `verified_user` for profile tests

**Fix:**

```python
# ❌ Bad
def test_get_profile(authenticated_client, user):
    # user might not have profile created

# ✅ Good
def test_get_profile(authenticated_client, verified_user):
    # verified_user has profile created
    url = reverse("user:my_profile")
    response = authenticated_client.get(url)
    assert response.status_code == 200
```

#### 3. Slow Test Execution

**Symptom:** Tests take too long to run

**Solutions:**

```bash
# Run tests in parallel
make test.parallel

# Skip slow tests
make test.fast

# Use --reuse-db flag (already in pytest.ini)
pytest --reuse-db

# Use --nomigrations flag (already in pytest.ini)
pytest --nomigrations
```

#### 4. Coverage Too Low

**Symptom:** Coverage below target

**Solution:**

```bash
# Check coverage report
make test.coverage

# Open HTML report to see missing lines
open htmlcov/index.html

# Focus on files with low coverage
# Add tests for uncovered lines
```

#### 5. Test Isolation Issues

**Symptom:** Tests pass individually but fail when run together

**Cause:** Shared state between tests

**Fix:**

```python
# ❌ Bad - Shared state
class TestUser:
    user = User.objects.create(...)  # Created once

# ✅ Good - Isolated fixtures
@pytest.fixture
def user(db):
    return User.objects.create(...)  # Created per test
```

#### 6. Database Errors

**Symptom:** DatabaseError or IntegrityError

**Solution:**

```python
# Ensure you use the db fixture
def test_something(db):  # Add db fixture
    user = User.objects.create(...)

# Or use transactional fixtures
@pytest.mark.django_db(transaction=True)
def test_something():
    ...
```

#### 7. JWT Token Issues

**Symptom:** Authentication fails in tests

**Fix:**

```python
# Use authenticated_client fixture (handles JWT automatically)
def test_protected_endpoint(authenticated_client):
    response = authenticated_client.get(url)
    assert response.status_code == 200

# Or create token manually
from rest_framework_simplejwt.tokens import RefreshToken

def test_with_manual_token(api_client, user):
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    response = api_client.get(url)
```

### Debugging Tips

```bash
# 1. Run specific test with verbose output
pytest -vv tests/unit/views/test_user_views.py::TestUserProfileView::test_get_profile

# 2. Show print statements
pytest -s

# 3. Stop on first failure
pytest -x

# 4. Show local variables in tracebacks
pytest -l

# 5. Re-run only failed tests
pytest --lf

# 6. Drop into debugger on failure
pytest --pdb

# 7. Show why tests were skipped
pytest -rs

# 8. Show slowest tests
pytest --durations=10
```

---

## 🔄 Migration Guide

### From Django Tests to Pytest

This project successfully migrated from Django's `TestCase` to pytest in October 2025.

#### Benefits Achieved

**Performance:**

- ✅ 50% faster execution (~2.6s vs ~5s previously)
- ✅ Parallel execution capability
- ✅ Selective test running with markers

**Developer Experience:**

- ✅ Cleaner test code with fixtures
- ✅ Better IDE integration
- ✅ More detailed failure output
- ✅ Easier debugging

**Code Quality:**

- ✅ Better test organization
- ✅ Reusable fixtures and mixins
- ✅ Parametrized tests (less duplication)

#### Comparison: Old vs New

**❌ Old Approach (JSON-based)**

```python
# tests/test_user.py
class UserTests(TestSetup):
    app_name = "user"

    def test_profile(self):
        self.run_tests(func_name=self.f_name)
```

**Problems:**

- Hard to debug when tests fail
- Unclear what each test does
- Dependent on JSON files
- Limited customization
- No IDE support

**✅ New Approach (Pytest-based)**

```python
# tests/unit/views/test_user_views.py
@pytest.mark.unit
class TestUserProfileView:
    """Test user profile view endpoints."""

    @pytest.fixture
    def url(self):
        return reverse("user:my_profile")

    def test_get_profile_authenticated(self, authenticated_client, verified_user, url):
        """Test getting profile with authentication."""
        response = authenticated_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == verified_user.username
        assert "password" not in response.data
```

**Benefits:**

- Clear what is being tested
- Easy to debug
- Flexible fixtures
- Great IDE support
- Can parametrize easily

#### Migration Steps (For Future Reference)

If you need to migrate more tests:

**Phase 1: Setup (Week 1)**

- [x] Install pytest packages
- [x] Create conftest.py with fixtures
- [x] Setup pytest.ini and .coveragerc
- [x] Create documentation

**Phase 2: Convert Tests (Week 2-3)**

- [x] Convert auth tests to pytest
- [x] Convert user tests to pytest
- [x] Add unit tests for models/views
- [x] Achieve baseline coverage (52.20%)

**Phase 3: Expand Coverage (Week 4+)**

- [ ] Add more unit tests (target: 70% of suite)
- [ ] Add integration tests (target: 25% of suite)
- [ ] Add E2E tests (target: 5% of suite)
- [ ] Achieve 80%+ coverage

**Phase 4: Optimize (Ongoing)**

- [ ] Optimize slow tests
- [ ] Setup CI/CD integration
- [ ] Regular maintenance

#### Legacy Tests (Deprecated)

The following are kept for reference but should NOT be used for new tests:

```
tests/test_case/
├── auth.json          # ⚠️ Deprecated - use pytest tests
├── user.json          # ⚠️ Deprecated - use pytest tests
└── data_init.json     # ⚠️ Deprecated
```

**Do not:**

- Add new JSON test cases
- Use `TestSetup.run_tests()` method
- Use Django's `TestCase` class

**Instead:**

- Write pytest-based tests
- Use fixtures from conftest.py
- Follow examples in `tests/unit/` and `tests/integration/`

---

## 📊 Analysis & Metrics

### Current Coverage Statistics

**Overall Project Coverage:** 52.20%

| Metric                 | Value        |
| ---------------------- | ------------ |
| **Total Statements**   | 1,293        |
| **Covered Statements** | 675          |
| **Missing Statements** | 618          |
| **Tests Passing**      | 12/12 (100%) |
| **Execution Time**     | ~2.6 seconds |

### Coverage by Module

| Module                         | Coverage | Status       | Priority          |
| ------------------------------ | -------- | ------------ | ----------------- |
| `core/common/admin.py`         | 94.55%   | ✅ Excellent | Maintain          |
| `configurations/urls.py`       | 89.47%   | ✅ Good      | Maintain          |
| `common/exceptions.py`         | 85.71%   | ✅ Good      | Maintain          |
| `core/user/views/user.py`      | 73.68%   | 🟡 Fair      | Improve           |
| `core/user/admin.py`           | 73.03%   | 🟡 Fair      | Improve           |
| `configurations/middleware.py` | 74.29%   | 🟡 Fair      | Improve           |
| `core/sites.py`                | 37.64%   | 🔴 Low       | **High priority** |
| `core/user/views/admin.py`     | 0.00%    | 🔴 None      | **High priority** |
| `configurations/telemetry.py`  | 0.00%    | 🔴 None      | **High priority** |

### Test Distribution

```
Current:
- Unit Tests: 5 (42%)
- Integration Tests: 7 (58%)
- E2E Tests: 0 (0%)

Target:
- Unit Tests: 70% of total tests
- Integration Tests: 25% of total tests
- E2E Tests: 5% of total tests
```

### Quality Metrics

| Metric              | Before Migration | After Migration | Improvement |
| ------------------- | ---------------- | --------------- | ----------- |
| Test Execution Time | ~5 seconds       | ~2.6 seconds    | 48% faster  |
| Code Coverage       | Unknown          | 52.20%          | ✅ Baseline |
| Number of Tests     | ~10              | 12              | +20%        |
| Test Confidence     | Medium           | High            | ✅ Improved |
| Debugging Time      | High             | Low             | ✅ Improved |

### Coverage Goals

**Short-term (1-2 months):**

- [ ] Increase overall coverage to 65%
- [ ] Add unit tests for all models
- [ ] Add unit tests for all serializers
- [ ] Cover critical user flows

**Mid-term (3-4 months):**

- [ ] Increase overall coverage to 75%
- [ ] Add performance tests
- [ ] Add E2E tests for critical journeys
- [ ] Optimize test execution time

**Long-term (6+ months):**

- [ ] Achieve 80%+ coverage
- [ ] Full CI/CD integration
- [ ] Automated coverage reporting
- [ ] Regular coverage monitoring

### Testing Philosophy

This project follows industry best practices:

1. **Test Pyramid**: 70% unit, 25% integration, 5% E2E
2. **Test-Driven Development**: Write tests first when possible
3. **Continuous Testing**: Run tests frequently during development
4. **Coverage as Guide**: Use coverage to find gaps, not as absolute metric
5. **Quality over Quantity**: Meaningful tests > high coverage number

### Historical Context

**October 28, 2025: Major Testing Migration**

Successfully migrated from Django's traditional testing framework to pytest:

**Changes:**

- Migrated from `unittest.TestCase` to pytest
- Created comprehensive fixture system (6 fixtures)
- Added reusable test mixins (4 mixins)
- Established baseline coverage (52.20%)
- Created 12 passing tests (100% pass rate)
- Improved execution time by 48%

**Documentation Created:**

- Testing Standards (this file)
- CHANGELOG.md with full migration history
- pytest.ini configuration
- .coveragerc configuration

---

## 📚 Additional Resources

### Documentation

- **[pytest Documentation](https://docs.pytest.org/)** - Official pytest docs
- **[pytest-django Documentation](https://pytest-django.readthedocs.io/)** - Django-specific pytest features
- **[Django Testing Best Practices](https://docs.djangoproject.com/en/stable/topics/testing/best-practices/)** - Django's testing guide
- **[Test Driven Development with Python](https://www.obeythetestinggoat.com/)** - Comprehensive TDD guide

### Project Files

- `pytest.ini` - Pytest configuration
- `.coveragerc` - Coverage configuration
- `tests/conftest.py` - Shared fixtures
- `tests/mixins.py` - Reusable test utilities
- `CHANGELOG.md` - Testing migration history

### Example Tests

- `tests/unit/models/test_user_model.py` - Model testing examples
- `tests/unit/views/test_user_views.py` - API testing examples
- `tests/integration/test_auth_flow.py` - Integration testing examples

### Makefile Commands

See all available test commands:

```bash
# In the project root
make help | grep test
```

---

## 🎓 Learning Path

### For New Developers

1. **Day 1: Setup & Basics**

   - Read this README (30 mins)
   - Install dependencies: `make i.dev pytest pytest-django`
   - Run tests: `make test`
   - Review example tests

2. **Day 2: Write First Test**

   - Pick a simple function to test
   - Write a unit test using examples as reference
   - Run your test: `make test.file tests/your_test.py`
   - Verify it passes

3. **Week 1: Practice**

   - Write 2-3 tests per day
   - Use fixtures from conftest.py
   - Try parametrized tests
   - Check coverage: `make test.coverage`

4. **Week 2: Advanced**
   - Write integration tests
   - Use test mixins
   - Mock external services
   - Optimize slow tests

### For Experienced Developers

1. Review pytest-specific features
2. Check fixture definitions in conftest.py
3. Review test organization structure
4. Start writing tests following established patterns

---

## ✅ Testing Checklist

When writing new tests, ensure:

- [ ] Test name describes what is being tested
- [ ] Test follows AAA pattern (Arrange-Act-Assert)
- [ ] Appropriate fixtures are used
- [ ] Proper markers are added (`@pytest.mark.unit`, etc.)
- [ ] Both success and error cases are tested
- [ ] External dependencies are mocked
- [ ] Coverage doesn't decrease
- [ ] Tests pass locally before committing
- [ ] Docstring explains what test does
- [ ] `format="json"` added to POST/PUT/PATCH requests
- [ ] Test is independent (doesn't rely on other tests)

---

## 🤝 Contributing

When adding new tests:

1. **Follow the structure**: Place tests in appropriate directories
2. **Use existing fixtures**: Check conftest.py before creating new ones
3. **Add markers**: Categorize tests with `@pytest.mark.unit` etc.
4. **Run tests locally**: `make test` before committing
5. **Check coverage**: `make test.coverage` to ensure no regression
6. **Update docs**: If adding new patterns, document them

---

**Last Updated:** November 3, 2025
**Testing Framework:** pytest 8.4.2
**Coverage:** 52.20% (targeting 80%+)
**Status:** ✅ All 12 tests passing
