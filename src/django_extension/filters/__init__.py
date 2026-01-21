import json
from typing import Optional

from django.core.exceptions import FieldError
from django.db.models import Q
from rest_framework import filters
from rest_framework.request import Request

__all__ = [
    'ModelFilter',
    'get_boolean_query_param',
]

class ModelFilter(
    filters.BaseFilterBackend
):
    """Common filter for model filters"""

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

def get_boolean_query_param(request: Request, label: str) -> Optional[bool]:
    """Recover boolean query param as bool"""
    param = request.query_params.get(label)
    if param is None:
        return None
    if isinstance(param, bool):
        return param
    if isinstance(param, str):
        return param.lower() == "true"
    return False
