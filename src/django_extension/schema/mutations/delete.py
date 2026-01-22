from typing import Optional

from django_extension.schema.permissions import GraphQLPermissions, GraphQLResolve
from graphene import Mutation, Boolean, ID

__all__ = ['ModelDeleteMutation']

class ModelDeleteMutation(Mutation):
    class Meta:
        abstract = True

    ok = Boolean()

    @classmethod
    def __init_subclass_with_meta__(
            cls,
            interfaces=(),
            resolver=None,
            output=None,
            arguments=None,
            model_class=None,
            _meta=None,
            permission: Optional[GraphQLPermissions] = None,
            **options
    ):
        cls.model_class = model_class
        cls.permission = permission
        super().__init_subclass_with_meta__(
            interfaces, resolver, output, arguments, _meta, **options
        )

    class Arguments:
        id = ID()

    @classmethod
    def mutate(cls, root, info, **kwargs):
        if cls.permission is not None:
            GraphQLResolve(permission=cls.permission).check_permission(info.context.user)

        obj = cls.model_class.objects.get(pk=kwargs["id"])
        obj.delete()
        return cls(ok=True)
