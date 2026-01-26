from typing import Optional

import graphene
from graphene_django_pagination import DjangoPaginationConnectionField

from .permissions import GraphQLPermissions, GraphQLResolve

__all__ = [
    'ByIdField',
    'AuthenticatedPaginationConnectionField'
]



class ByIdField(graphene.Field):

    def __init__(
            self,
            type_,
            args=None,
            permission: Optional[GraphQLPermissions] = None,
            *extra_args,
            **kwargs,
    ):
        self.permission = permission
        super().__init__(type_, args, id=graphene.ID(required=True), resolver=self.resolve, *extra_args, **kwargs)

    def resolve(self, _, info, id: int):
        if self.permission is not None:
            GraphQLResolve(permission=self.permission).check_permission(
                info.context.user
            )

        return self.type.get_node(info, id)

class AuthenticatedPaginationConnectionField(DjangoPaginationConnectionField):
    """Extended DjangoPaginationConnectionField - Only allow authenticated queries"""

    @classmethod
    def resolve_queryset(
        cls, connection, iterable, info, args, filtering_args, filterset_class
    ):
        GraphQLResolve(permission=GraphQLPermissions.AUTHENTICATED).check_permission(
            info.context.user
        )

        return super().resolve_queryset(
            connection, iterable, info, args, filtering_args, filterset_class
        )
