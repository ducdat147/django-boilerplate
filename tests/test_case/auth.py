from rest_framework import status
from django.urls import reverse

from tests.test_case.data_init import DATA_INIT


AUTH_TEST_CASE = {
    "test_auth.test_register_user": {
        "path_name": reverse("register"),
        "method": "post",
        "test_case": [
            {
                "request_body": {
                    "email": "newusertest@yopmail.com",
                    "password": "1StrongPassword!",
                },
                "status_code": status.HTTP_201_CREATED,
                "fields": [],
                "format": "json",
                "response_body": {
                    "email": "newusertest@yopmail.com",
                    "message": "User registered successfully",
                    "is_existed": False,
                },
            },
        ],
    },
    "test_auth.test_login": {
        "path_name": reverse("token-obtain-pair"),
        "method": "post",
        "test_case": [
            {
                "request_body": {
                    "username": DATA_INIT["email"],
                    "password": DATA_INIT["password"],
                },
                "status_code": status.HTTP_200_OK,
                "fields": ["refresh", "access"],
            },
            {
                "request_body": {
                    "username": "no_exist_user@yopmail.com",
                    "password": "1StrongPassword!",
                },
                "status_code": status.HTTP_401_UNAUTHORIZED,
            },
            {
                "request_body": {
                    "username": "test@yopmail.com",
                    "password": "wrongpassword",
                },
                "status_code": status.HTTP_401_UNAUTHORIZED,
            },
        ],
    },
}
