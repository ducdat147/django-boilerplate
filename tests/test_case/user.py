from rest_framework import status

from tests.test_case.data_init import DATA_INIT

USER_TEST_CASE = {
    "test_user.test_profile": {
        "path_name": "user:my_profile",
        "method": "get",
        "test_case": [
            {
                "request_body": {},
                "status_code": status.HTTP_200_OK,
                "fields": [
                    "id",
                    "username",
                    "email",
                    "is_email_verified",
                    "phone",
                    "is_phone_verified",
                    "first_name",
                    "last_name",
                    "full_name",
                    "date_of_birth",
                    "gender",
                    "address",
                ],
                "format": "json",
                "response_body": {
                    "username": DATA_INIT["username"],
                    "email": DATA_INIT["email"],
                    "phone": DATA_INIT["phone"],
                },
            },
        ],
    },
    "test_user.test_update_profile": {
        "path_name": "user:my_profile",
        "method": "patch",
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
                    "username": DATA_INIT["username"],
                    "email": DATA_INIT["email"],
                    "phone": DATA_INIT["phone"],
                },
            },
        ],
    },
    "test_user.test_reset_password": {
        "path_name": "user:reset_password",
        "method": "post",
        "test_case": [
            {
                "request_body": {
                    "old_password": DATA_INIT["password"],
                    "new_password": DATA_INIT["password"] + "1",
                },
                "status_code": status.HTTP_204_NO_CONTENT,
                "format": "json",
                "response_body": {},
            },
            {
                "request_body": {
                    "old_password": DATA_INIT["password"],
                    "new_password": DATA_INIT["password"] + "1",
                },
                "status_code": status.HTTP_400_BAD_REQUEST,
                "format": "json",
                "response_body": {},
            },
            {
                "request_body": {
                    "old_password": DATA_INIT["password"] + "1",
                    "new_password": "1",
                },
                "status_code": status.HTTP_400_BAD_REQUEST,
                "format": "json",
                "response_body": {},
            },
        ],
    },
}
