from typing import Optional

from django_extension.schema.permissions import GraphQLPermissions, GraphQLResolve
from graphene_django.forms.mutation import DjangoModelFormMutation


__all__ = [
    "ExtendedModelFormMutation",
]

class ExtendedModelFormMutation(DjangoModelFormMutation):
    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, form_class=None, model=None, return_field_name=None, only_fields=(),
                                    permission: Optional[GraphQLPermissions] = None,
                                    exclude_fields=(), **options):
        cls.permission = permission
        super().__init_subclass_with_meta__(form_class, model, return_field_name, only_fields, exclude_fields,
                                            **options)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        if cls.permission is not None:
            GraphQLResolve(permission=cls.permission).check_permission(info.context.user)
        return super().mutate_and_get_payload(root, info, **input)

    @classmethod
    def get_form_kwargs(cls, root, info, **input):
        pk = input.get("id", None)

        kwargs = super().get_form_kwargs(root, info, **input)
        if (
                pk
                and cls._meta.model
                and hasattr(cls._meta.model.objects, "get_editable_or_fail")
        ):
            kwargs["instance"] = cls._meta.model.objects.get_editable_or_fail(
                user=info.context.user,
                pk=pk,
            )

        return kwargs
