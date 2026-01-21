from graphene import relay

__all__ = ['ExtendedInterface']

class ExtendedInterface(relay.Node):
    """
    For fetching object id instead of Node id
    """

    class Meta:
        name = "ExtendedInterface"

    @classmethod
    def to_global_id(cls, type_, id):
        return id
