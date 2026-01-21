from django.db.models import TextChoices

from .constraints import NoSelfParentConstraint
from .queryset import ExtendedQuerySet

__all__ = [
    # Constraint
    'NoSelfParentConstraint',

    # QuerySet
    'ExtendedQuerySet',

    'ExtendedEnum',
]


class ExtendedEnum(TextChoices):
    """Enum model field"""

    @classmethod
    def from_label(cls, label: str):
        """Get enum from label"""
        return cls.values[cls.labels.index(label)]
