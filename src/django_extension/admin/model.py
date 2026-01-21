from typing import Type

from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Model, QuerySet
from django.utils.safestring import mark_safe
from rest_framework.serializers import ModelSerializer

__all__ = [
    'ExtendedModelAdmin',
    'HiddenModelAdmin',
    'JSONExportModelAdmin',
]


class JSONExportModelAdmin(admin.ModelAdmin):
    serializer: Type[ModelSerializer] = None
    model: Type[Model] = None
    depth: int = 0

    actions = [
        "export",
    ]

    @admin.action(description="Download data as JSON")
    def export(self, request: WSGIRequest, queryset: QuerySet):
        """Export JSON file containing serialized queryset"""
        path = request.path.split("/")
        path.pop()
        filename = path.pop()

        serialized_data: ModelSerializer
        if serializer is None:
            SimpleSerializer.Meta.model = model
            SimpleSerializer.Meta.depth = depth
            serialized_data = SimpleSerializer(data=queryset, many=True)
        else:
            serialized_data = serializer(data=queryset, many=True)
        serialized_data.is_valid()
        response = JsonResponse(
            data=serialized_data.data, safe=False, json_dumps_params={"ensure_ascii": False}
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}.json"'


class ExtendedModelAdmin(admin.ModelAdmin):

    # noinspection PyMethodMayBeStatic
    def safe_list(self, array: [str]) -> str:
        if len(array) == 0:
            return self.get_empty_value_display()
        return mark_safe("<br/>".join(array))

    # noinspection PyMethodMayBeStatic
    def safe_queryset(self, queryset: QuerySet) -> str:
        if queryset.count() == 0:
            return self.get_empty_value_display()
        return mark_safe("<br/>".join([str(i) for i in queryset]))


class HiddenModelAdmin(admin.ModelAdmin):

    def has_module_permission(self, request):
        # Hide it from admin but enable autocomplete field and creation
        return False
