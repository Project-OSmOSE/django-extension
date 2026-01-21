from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django_extension.schema.errors import NotFoundError, ForbiddenError

__all__ = [
    'ExtendedQuerySet',
]

class ExtendedQuerySet(models.QuerySet):
    def filter_viewable_by(self, user, **kwargs):
        return self.filter(**kwargs)

    def filter_editable_by(self, user, **kwargs):
        return self.filter(**kwargs)

    def get_viewable_or_fail(self, user, **kwargs):
        try:
            return self.filter_viewable_by(user=user, **kwargs).get(**kwargs)
        except ObjectDoesNotExist as exc:
            raise NotFoundError() from exc

    def get_editable_or_fail(self, user, **kwargs):
        self.get_viewable_or_fail(user=user, **kwargs)

        try:
            return self.filter_editable_by(user=user, **kwargs).get(**kwargs)
        except ObjectDoesNotExist as exc:
            raise ForbiddenError() from exc
