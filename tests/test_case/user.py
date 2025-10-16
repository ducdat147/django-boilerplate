from rest_framework import status

from tests.test_case.data_init import DATA_INIT


USER_TEST_CASE = {
    "test_user.test_profile": {
        "path_name": "my-profile",
        "method": "get",
        "test_case": [
            {
                "request_body": {},
                "status_code": status.HTTP_200_OK,
                "fields": ["id", "username", "email"],
                "format": "json",
                "response_body": {
                    "username": DATA_INIT["email"],
                    "email": DATA_INIT["email"],
                },
            },
        ],
    },
    "test_user.test_update_profile": {
        "path_name": "my-profile",
        "method": "put",
        "test_case": [
            {
                "request_body": {
                    "email": DATA_INIT["email"],
                    "phone": DATA_INIT["phone"],
                },
                "status_code": status.HTTP_200_OK,
                "fields": ["id", "username", "email", "phone"],
                "format": "json",
                "response_body": {
                    "username": DATA_INIT["email"],
                    "email": DATA_INIT["email"],
                    "phone": DATA_INIT["phone"],
                },
            },
        ],
    },
}
