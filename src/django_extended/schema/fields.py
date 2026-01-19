import graphene


__all__ = [
    'ByIdField'
]

class ByIdField(graphene.Field):

    def __init__(self, type_, args=None, *extra_args, **kwargs):
        super().__init__(type_, args, id=graphene.ID(required=True), resolver=self.resolve, *extra_args, **kwargs)

    def resolve(self, info, id: int):
        return self.type.get_node(info, id)
