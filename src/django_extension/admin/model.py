from typing import Type, Optional, Callable

from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Model, QuerySet
from django.http import JsonResponse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django_extension.serializers import SimpleSerializer
from rest_framework.reverse import reverse
from rest_framework.serializers import ModelSerializer

__all__ = [
    "ExtendedModelAdmin",
]


class ExtendedModelAdmin(admin.ModelAdmin):
    # To enable JSON export: fill add:
    # actions = ["export",]
    serializer: Type[ModelSerializer] = None
    depth: int = 0

    # Hide in admin menu
    hidden: bool = False

    def safe_list(self, array: [str]) -> str:
        if len(array) == 0:
            return self.get_empty_value_display()
        return mark_safe("<br/>".join(array))

    @staticmethod
    def _get_edit_link(obj: Model, to_str: Callable[[Model], str] = lambda x: str(x)):
        app = obj._meta.app_label
        model = obj._meta.model_name
        view = f"admin:{app}_{model}_change"
        link = reverse(view, args=[obj.pk])
        return format_html('<a href="{}">{}</a>', link, to_str(obj))

    def display_foreign_key(
        self,
        obj: Optional[Model],
        allow_edit: bool = False,
        to_str: Callable[[Model], str] = lambda x: str(x),
    ) -> str:
        if obj is None:
            return self.get_empty_value_display()
        if allow_edit:
            return ExtendedModelAdmin._get_edit_link(obj)
        else:
            return to_str(obj)

    def list_queryset(
        self,
        queryset: QuerySet,
        allow_edit: bool = False,
        to_str: Callable[[Model], str] = lambda x: str(x),
    ) -> str:
        if queryset.count() == 0:
            return self.get_empty_value_display()
        items = []
        for obj in queryset:
            if allow_edit:
                items.append(ExtendedModelAdmin._get_edit_link(obj))
            else:
                items.append(to_str(obj))
        return mark_safe("<br/>".join(items))

    # Manage display in admin menu
    def has_module_permission(self, request):
        # Hide it from admin but enable autocomplete field and creation
        return not self.hidden

    @admin.action(description="Download data as JSON")
    def export(self, request: WSGIRequest, queryset: QuerySet):
        """Export JSON file containing serialized queryset"""
        path = request.path.split("/")
        path.pop()
        filename = path.pop()

        serialized_data: ModelSerializer
        if self.serializer is None:
            SimpleSerializer.Meta.model = self.model
            SimpleSerializer.Meta.depth = self.depth
            serialized_data = SimpleSerializer(data=queryset, many=True)
        else:
            serialized_data = self.serializer(data=queryset, many=True)
        serialized_data.is_valid()
        response = JsonResponse(
            data=serialized_data.data,
            safe=False,
            json_dumps_params={"ensure_ascii": False},
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}.json"'
        return response
