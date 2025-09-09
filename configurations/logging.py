from copy import deepcopy
from typing import Any


HIDDEN_FIELDS = [
    "password",
    "refresh",
    "access",
    "token",
]


def _sanitize_recursive(
    data: dict[str, Any],
    hidden_fields: list[str] = HIDDEN_FIELDS,
    mask_value: str = "****",
    case_sensitive: bool = False,
    deep_search: bool = True,
) -> Any:
    if isinstance(data, dict):
        for key, value in data.items():
            # Check if current key should be hidden
            key_to_check = key.lower() if not case_sensitive else key
            fields_to_check = [
                f.lower() if not case_sensitive else f for f in hidden_fields
            ]

            if key_to_check in fields_to_check:
                data[key] = mask_value
            elif deep_search and isinstance(value, (dict, list)):
                data[key] = _sanitize_recursive(value)

    elif isinstance(data, list):
        return [_sanitize_recursive(item) for item in data]

    return data


def sanitize_data(
    data: dict[str, Any],
    hidden_fields: list[str] = HIDDEN_FIELDS,
    mask_value: str = "****",
    case_sensitive: bool = False,
    deep_search: bool = True,
) -> dict[str, Any]:
    """
    Sanitize dictionary data by hiding sensitive fields

    Args:
        data: Input dictionary to sanitize
        hidden_fields: List of field names to hide (default: HIDDEN_FIELDS)
        mask_value: Value to replace sensitive data with
        case_sensitive: Whether field matching is case sensitive
        deep_search: Whether to search nested dictionaries recursively

    Returns:
        Sanitized dictionary with sensitive fields masked
    """
    if not bool(hidden_fields):
        return data

    # Create a deep copy to avoid modifying original data
    sanitized_data = deepcopy(data)

    return _sanitize_recursive(
        sanitized_data,
        hidden_fields,
        mask_value,
        case_sensitive,
        deep_search,
    )
