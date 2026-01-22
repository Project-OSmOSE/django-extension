from collections import OrderedDict
from typing import Optional

import graphene
from django.db.models import QuerySet
from django_extension.schema.permissions import GraphQLResolve, GraphQLPermissions
from django_extension.schema.types.enum import get_global_enum_registry
from django_extension.serializers import EnumField
from graphene import InputField, ClientIDMutation, InputObjectType
from graphene.types.utils import yank_fields_from_attrs
from graphene_django.registry import get_global_registry
from graphene_django.rest_framework.mutation import (
    SerializerMutationOptions,
)
from graphene_django.rest_framework.serializer_converter import (
    get_graphene_type_from_serializer_field,
)
from graphene_django.types import ErrorType
from rest_framework import serializers
from rest_framework.serializers import BaseSerializer

__all__ = ['ListSerializerMutation']


def convert_serializer_field(
        field, is_input=True, convert_choices_to_enum=True, force_optional=False
):
    """
    Converts a django rest frameworks field to a graphql field
    and marks the field as required if we are creating an input type
    and the field itself is required
    """

    if isinstance(field, serializers.ChoiceField) and not convert_choices_to_enum:
        graphql_type = graphene.String
    elif isinstance(field, EnumField):
        enum_registry = get_global_enum_registry()
        graphql_type = enum_registry.get_type_for_enum(field.enum)
    else:
        graphql_type = get_graphene_type_from_serializer_field(field)


    args = []
    kwargs = {
        "description": field.help_text,
        "required": is_input and field.required and not force_optional,
    }

    # if it is a tuple or a list it means that we are returning
    # the graphql type and the child type
    if isinstance(graphql_type, (list, tuple)):
        kwargs["of_type"] = graphql_type[1]
        graphql_type = graphql_type[0]

    if isinstance(field, serializers.ModelSerializer):
        if is_input:
            graphql_type = convert_serializer_to_input_type(field.__class__)
        else:
            global_registry = get_global_registry()
            field_model = field.Meta.model
            args = [global_registry.get_type_for_model(field_model)]
    elif isinstance(field, serializers.ListSerializer):
        field = field.child
        if is_input:
            kwargs["of_type"] = convert_serializer_to_input_type(field.__class__)
        else:
            del kwargs["of_type"]
            global_registry = get_global_registry()
            field_model = field.Meta.model
            args = [global_registry.get_type_for_model(field_model)]

    return graphql_type(*args, **kwargs)


def convert_serializer_to_input_type(serializer_class):
    cached_type = convert_serializer_to_input_type.cache.get(
        serializer_class.__name__, None
    )
    if cached_type:
        return cached_type
    serializer = serializer_class()

    items = {
        name: convert_serializer_field(field)
        for name, field in serializer.fields.items()
    }
    ret_type = type(
        f"{serializer.__class__.__name__}Input",
        (graphene.InputObjectType,),
        items,
    )
    convert_serializer_to_input_type.cache[serializer_class.__name__] = ret_type
    return ret_type


convert_serializer_to_input_type.cache = {}


def fields_for_serializer(
        serializer,
        only_fields,
        exclude_fields,
        is_input=False,
        convert_choices_to_enum=True,
        lookup_field=None,
        optional_fields=(),
):
    fields = OrderedDict()
    for name, field in serializer.fields.items():
        is_not_in_only = only_fields and name not in only_fields
        is_excluded = any(
            [
                name in exclude_fields,
                field.write_only
                and not is_input,  # don't show write_only fields in Query
                field.read_only
                and is_input
                and lookup_field != name,  # don't show read_only fields in Input
                isinstance(
                    field, serializers.HiddenField
                ),  # don't show hidden fields in Input
            ]
        )

        if is_not_in_only or is_excluded:
            continue
        is_optional = name in optional_fields or "__all__" in optional_fields

        fields[name] = convert_serializer_field(
            field,
            is_input=is_input,
            convert_choices_to_enum=convert_choices_to_enum,
            force_optional=is_optional,
        )
    return fields


class ListSerializerMutation(ClientIDMutation):
    class Meta:
        abstract = True

    errors = graphene.List(
        graphene.List(
            ErrorType, description="May contain more than one error for same field."
        )
    )

    @classmethod
    def __init_subclass_with_meta__(
            cls,
            lookup_field=None,
            serializer_class=None,
            model_class=None,
            model_operations=("create", "update"),
            only_fields=(),
            exclude_fields=(),
            convert_choices_to_enum=False,
            _meta=None,
            optional_fields=(),
            **options,
    ):
        if not serializer_class:
            # pylint: disable=broad-exception-raised
            raise Exception("serializer_class is required for the SerializerMutation")

        if "update" not in model_operations and "create" not in model_operations:
            # pylint: disable=broad-exception-raised
            raise Exception('model_operations must contain "create" and/or "update"')

        serializer = serializer_class()
        if model_class is None:
            serializer_meta = getattr(serializer_class, "Meta", None)
            if serializer_meta:
                model_class = getattr(serializer_meta, "model", None)

        if lookup_field is None and model_class:
            lookup_field = model_class._meta.pk.name

        SerializerInput = type(
            f"{model_class.__name__}Input",
            (InputObjectType,),
            dict(
                yank_fields_from_attrs(
                    fields_for_serializer(
                        serializer,
                        only_fields,
                        exclude_fields,
                        is_input=True,
                        convert_choices_to_enum=convert_choices_to_enum,
                        lookup_field=lookup_field,
                        optional_fields=optional_fields,
                    ),
                    _as=InputField,
                )
            ),
        )
        input_fields = {"list": graphene.List(SerializerInput, required=True)}

        if not _meta:
            _meta = SerializerMutationOptions(cls)
        _meta.lookup_field = lookup_field
        _meta.model_operations = model_operations
        _meta.serializer_class = serializer_class
        _meta.model_class = model_class

        input_fields = yank_fields_from_attrs(input_fields, _as=InputField)
        super().__init_subclass_with_meta__(
            _meta=_meta, input_fields=input_fields, **options
        )

    @classmethod
    def get_serializer_context(cls, root, info, **input) -> dict:
        """Get serializer context value"""
        return {}

    @classmethod
    def get_serializer_queryset(cls, root, info, **input) -> Optional[QuerySet]:
        """Get serializer queryset"""
        return None

    @classmethod
    def get_serializer_kwargs(cls, root, info, **input):
        return {
            "instance": cls.get_serializer_queryset(root, info, **input),
            "data": input["list"],
            "many": True,
            "context": {
                **cls.get_serializer_context(root, info, **input),
                "request": info.context,
            },
        }

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        GraphQLResolve(permission=GraphQLPermissions.AUTHENTICATED).check_permission(
            info.context.user
        )
        kwargs = cls.get_serializer_kwargs(root, info, **input)
        serializer: BaseSerializer = cls._meta.serializer_class(**kwargs)

        if serializer.is_valid():
            serializer.save()
            return cls(errors=None)
        errors = []
        for e in serializer.errors:
            errors.append(ErrorType.from_errors(e))
        return cls(errors=errors)
