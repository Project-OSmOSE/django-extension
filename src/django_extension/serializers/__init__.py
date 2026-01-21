from django.db import transaction
from django.db.models import QuerySet
from rest_framework import serializers

from .fields import (
    EnumField,
)

__all__ = [
    # Fields
    'EnumField',

    # serializers
    'SimpleSerializer'
    'ListSerializer'
]


class SimpleSerializer(serializers.ModelSerializer):
    """Serializer meant to output basic data"""

    class Meta:
        model = None
        fields = "__all__"

class ListSerializer(serializers.ListSerializer):
    """Default list serializer -> will update corresponding ids,
    remove extra items in queryset and create extra items in data"""

    def get_serializer_data(self, data: dict) -> dict:
        """Get serialized data"""
        return self.child.__class__(data).data

    @transaction.atomic()
    def update(self, instance: QuerySet, validated_data: list[dict]):
        serializer_list: [Serializer] = []
        for data in validated_data:
            serializer_data = self.get_serializer_data(data)
            if "id" in data and data["id"] is not None:
                update_instance = instance.filter(id=data["id"])
                if update_instance.exists():
                    serializer_list.append(
                        self.child.__class__(
                            instance=update_instance.first(),
                            data=serializer_data,
                            context=self.context,
                        )
                    )
                    continue
            serializer_list.append(
                self.child.__class__(data=serializer_data, context=self.context)
            )
        serializer: Serializer
        for serializer in serializer_list:
            serializer.is_valid(raise_exception=True)

        result_instances = []
        for serializer in serializer_list:
            serializer.save()
            result_instances.append(serializer.instance)
        instance.exclude(id__in=[r.id for r in result_instances]).delete()
        return result_instances

