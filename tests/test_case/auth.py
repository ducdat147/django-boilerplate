from rest_framework import status

from tests.test_case.data_init import DATA_INIT

AUTH_TEST_CASE = {
    "test_auth.test_register_user": {
        "path_name": "auth:register",
        "method": "post",
        "test_case": [
            {
                "request_body": {
                    "username": "newusertest2",
                    "email": "newusertest2@yopmail.com",
                    "password": "1StrongPassword!",
                    "phone": "+84989000001",
                },
                "status_code": status.HTTP_201_CREATED,
                "fields": ["refresh", "access"],
            },
            {
                "request_body": {
                    "username": "newusertest3",
                    "email": "newusertest3@yopmail.com",
                    "password": "1234",
                    "phone": "+84989000002",
                },
                "status_code": status.HTTP_400_BAD_REQUEST,
            },
        ],
    },
    "test_auth.test_register_user__login": {
        "path_name": "auth:token_obtain_pair",
        "method": "post",
        "test_case": [
            {
                "request_body": {
                    "username": "newusertest2",
                    "password": "1StrongPassword!",
                },
                "status_code": status.HTTP_200_OK,
                "fields": ["refresh", "access"],
            },
        ],
    },
    "test_auth.test_login": {
        "path_name": "auth:token_obtain_pair",
        "method": "post",
        "test_case": [
            {
                "request_body": {
                    "username": DATA_INIT["username"],
                    "password": DATA_INIT["password"],
                },
                "status_code": status.HTTP_200_OK,
                "fields": ["refresh", "access"],
            },
            {
                "request_body": {
                    "username": "no_exist_user",
                    "password": DATA_INIT["password"],
                },
                "status_code": status.HTTP_401_UNAUTHORIZED,
            },
            {
                "request_body": {
                    "username": DATA_INIT["username"],
                    "password": "wrongpassword",
                },
                "status_code": status.HTTP_401_UNAUTHORIZED,
            },
        ],
    },
    "test_auth.test_refresh_token__invalid": {
        "path_name": "auth:token_refresh",
        "method": "post",
        "test_case": [
            {
                "request_body": {
                    "refresh": "invalidtoken",
                },
                "status_code": status.HTTP_401_UNAUTHORIZED,
            },
        ],
    },
}
