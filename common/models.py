from django.db import models


class BaseModel(models.Model):
    """
    An abstract base model that provides created and updated timestamps.

    Attributes:
        created_at (DateTimeField): The timestamp when the record was created.
        updated_at (DateTimeField): The timestamp when the record was last updated.
    """

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
