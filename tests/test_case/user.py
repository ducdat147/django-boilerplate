from rest_framework import status
from django.urls import reverse

from tests.test_case.data_init import DATA_INIT


USER_TEST_CASE = {
    "test_user.test_profile": {
        "path_name": reverse("my-profile"),
        "method": "get",
        "test_case": [
            {
                "request_body": {},
                "status_code": status.HTTP_200_OK,
                "fields": ["id", "username", "email", "first_name", "last_name"],
                "format": "json",
                "response_body": {
                    "username": DATA_INIT["email"],
                    "email": DATA_INIT["email"],
                },
            },
        ],
    },
}
