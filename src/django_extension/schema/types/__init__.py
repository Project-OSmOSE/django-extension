from .enum import ExtendedEnumType

__all__ = [
    # Enum
    'ExtendedEnumType',

    'ExtendedNode',
]

from django.db.models import QuerySet
from django_extension.schema.interfaces import ExtendedInterface
import graphene_django_optimizer
from graphql import GraphQLResolveInfo
from graphene_django import DjangoObjectType


class ExtendedNode(DjangoObjectType):
    """Base object type"""

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, model=None, registry=None, skip_registry=False, only_fields=None, fields=None,
                                    exclude_fields=None, exclude=None, filter_fields=None, filterset_class=None,
                                    connection=None, connection_class=None, use_connection=None, interfaces=(),
                                    convert_choices_to_enum=None, _meta=None, **options):
        super().__init_subclass_with_meta__(model, registry, skip_registry, only_fields, fields, exclude_fields,
                                            exclude, filter_fields, filterset_class, connection, connection_class,
                                            use_connection, interfaces + (ExtendedInterface,), convert_choices_to_enum,
                                            _meta, **options)

    @classmethod
    def resolve_queryset(cls, queryset: QuerySet, info: GraphQLResolveInfo):
        """Resolve Queryset"""
        if hasattr(queryset, "filter_viewable_by"):
            return queryset.filter_viewable_by(
                user=info.context.user,
            )
        return queryset

    @classmethod
    def get_queryset(cls, queryset: QuerySet, info: GraphQLResolveInfo):
        """Get Queryset"""
        return graphene_django_optimizer.query(
            cls.resolve_queryset(queryset, info), info
        )
