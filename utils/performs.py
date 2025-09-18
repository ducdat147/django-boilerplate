import importlib
import logging


logger = logging.getLogger(__name__)


class ConstanceValue:
    def __init__(self, field: str, meta_data: dict):
        self.field = field
        self.meta_data = meta_data

    def value(self, value):
        return self.meta_data.get(value, self.meta_data.get("default"))


def get_class_from_string(class_path: str):
    """
    Retrieves a Python class object from its string path.

    Args:
        class_path: The full string path to the class (e.g., "my_module.MyClass").

    Returns:
        The class object.

    Raises:
        ImportError: If the module cannot be imported.
        AttributeError: If the class is not found within the module.
    """
    if "." not in class_path:
        logger.error("Class path must include module name.")
        raise ValueError(
            "Class path must include module name, e.g., 'my_module.MyClass'"
        )
    try:
        module_name, class_name = class_path.rsplit(".", 1)
        module = importlib.import_module(module_name)
        class_obj = getattr(module, class_name)
        return class_obj
    except ImportError as e:
        logger.exception(e)
        raise ImportError(f"Module '{module_name}' could not be imported.") from e
