# Tests Documentation

## Overview
This directory contains all test files for the Django boilerplate project.

## Structure
```
tests/
├── README.md           # This documentation
├── test_case/          # Base test cases and utilities
│   ├── __init__.py     # Init file for test_case package
│   ├── data_init.py    # Test data initialization
│   ├── auth.py         # Authentication test cases
│   └── ...             # Other test case files
├── __init__.py
├── test_setup.py       # Test setup and utilities
├── test_auth.py        # Test file for authentication
└── ...                 # Other test files
```

## Running Tests

### Run all tests
```bash
python manage.py test
```

### Run specific test file
```bash
python manage.py test tests.test_models
```

### Run with coverage
```bash
coverage run manage.py test
coverage report
```

## Test Guidelines

### Defined Test Cases
- Create files `<module_name>.py` in folder `tests/test_case/` for each module to be tested like examples:
    ```python
    from rest_framework import status


    EXAMPLE_TEST_CASE = {
        "<test_filename>.<test_function_name>": {
            "path_name": "example-path",  # URL path name, use reverse() to get the URL
            "method": "get",  # HTTP method to use ["get", "post", "put", "patch", "delete"]
            "test_case": [  # List of test cases
                {
                    "request_body": {  # Request payload
                        "example_key": "example_value",
                        "another_key": "another_value"
                    },
                    "status_code": status.HTTP_200_OK,  # Expected HTTP status code
                    "fields": ["example_field"],  # Fields to check in the response
                    "format": "json",  # Format of the request
                    "response_body": {  # Expected response payload
                        "example_field": "example_value",
                    },
                },
            ],
        },
    }
    ```
- Add variables to `ALL_TEST_CASE` in `tests/test_case/__init__.py` to include the new test cases.
- Create test files `test_<module_name>.py` in folder `tests/` to run the tests like examples:
    ```python
    from tests.test_setup import TestSetup


    class AuthTests(TestSetup):
        def test_function_name(self):
            self.run_tests(func_name="test_filename.test_function_name")

    ```
