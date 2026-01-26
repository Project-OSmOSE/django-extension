from django_extension.schema.errors import NotFoundError

from .enum import ExtendedEnumType

__all__ = [
    # Enum
    'ExtendedEnumType',

    'ExtendedNode',
]

from typing import Optional

from django.db.models import QuerySet
from django_extension.schema.interfaces import ExtendedInterface
from graphene_django.types import DjangoObjectTypeOptions
import graphene_django_optimizer
from graphql import GraphQLResolveInfo
from graphene_django import DjangoObjectType
from rest_framework.request import Request


class ModelContextFilter:
    """Base context filter"""

    @classmethod
    def get_queryset(cls, context: Request):
        return QuerySet().none()

    @classmethod
    def get_edit_node_or_fail(cls, context: Request, pk: int):
        """Get node with edit rights or fail depending on the context"""
        raise NotFoundError()


class ExtendedObjectTypeMeta(DjangoObjectTypeOptions):
    context_filter: Optional[ModelContextFilter.__class__] = None


class OldExtendedNode(DjangoObjectType):
    """Base object type"""

    class Meta:
        abstract = True


    @classmethod
    def __init_subclass_with_meta__(
            cls,
            context_filter: Optional[ModelContextFilter.__class__] = None,
            _meta=None,
            **kwargs,
    ):
        if not _meta:
            _meta = ExtendedObjectTypeMeta(cls)
        if context_filter is not None:
            _meta.context_filter = context_filter
        super().__init_subclass_with_meta__(_meta=_meta, **kwargs)

    @classmethod
    def resolve_queryset(cls, queryset: QuerySet, info: GraphQLResolveInfo):
        """Resolve Queryset"""
        if cls._meta.context_filter is None:
            return queryset
        return cls._meta.context_filter.get_queryset(info.context, queryset=queryset)

    @classmethod
    def get_queryset(cls, queryset: QuerySet, info: GraphQLResolveInfo):
        """Get Queryset"""
        return graphene_django_optimizer.query(
            cls.resolve_queryset(queryset, info), info
        )


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
                                            use_connection, interfaces + (ExtendedInterface,), convert_choices_to_enum, _meta, **options)

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


