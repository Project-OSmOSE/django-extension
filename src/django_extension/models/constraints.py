from django.db.models import CheckConstraint, F, Q

__all__ = [
    'NoSelfParentConstraint'
]

class NoSelfParentConstraint(CheckConstraint):
    def __init__(self, name:str, **kwargs):
        super().__init__(name=name, check=~Q(parent_id=F("id")))
