import json

JSON_FILE = [
    "auth.json",
    "user.json",
]

ALL_TEST_CASE = {}
DATA_INIT = None

for item in JSON_FILE:
    with open(f"tests/test_case/{item}", "r") as f:
        ALL_TEST_CASE.update(json.load(f))

with open("tests/test_case/data_init.json", "r") as f:
    DATA_INIT = json.load(f)

__all__ = [
    "ALL_TEST_CASE",
    "DATA_INIT",
]
