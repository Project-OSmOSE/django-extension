import json

from django.core.exceptions import FieldError
from django.db.models import Q
from rest_framework import filters
from rest_framework.request import Request


__all__ = [
    'ModelFilter',
]

class ModelFilter(
    filters.SearchFilter,
):
    """Common filter for model viewsets"""

    def filter_queryset(self, request: Request, queryset, view):
        _queryset = super().filter_queryset(request, queryset, view)
        for param in request.query_params:
            try:
                value = request.query_params[param]
                key = param
                is_negation = param[-1] == "!"
                if is_negation:
                    key = param[:-1]
                try:
                    filter = Q(**{key: json.loads(value)})
                    if is_negation:
                        filter = ~filter
                    _queryset = _queryset.filter(filter)
                except (json.JSONDecodeError, TypeError):
                    filter = Q(**{key: value})
                    if is_negation:
                        filter = ~filter
                    _queryset = _queryset.filter(filter)
            except FieldError:
                continue
        return _queryset.distinct()
