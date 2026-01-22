import graphene

__all__ = ['ExtendedEnumType', 'get_global_enum_registry']

class ExtendedEnumType(graphene.Enum):

    mapping = {}

    class Meta:
        abstract = True

    @classmethod
    def __init_subclass_with_meta__(cls, enum=None, _meta=None, **options):
        enum_registry = get_global_enum_registry()
        enum_registry.register(cls, enum)
        super().__init_subclass_with_meta__(None, _meta, **options)

    @classmethod
    def get_type(cls):
        return super().get_type()

    def Field(self):
        return super().Field()


class EnumRegistry:

    def __init__(self):
        self._registry = {}

    def register(self, cls, enum):

        assert issubclass(
            cls, ExtendedEnumType
        ), f'Only ExtendedEnumType can be registered, received "{cls.__name__}"'
        if not getattr(cls._meta, "skip_registry", False):
            self._registry[enum] = cls

    def get_type_for_enum(self, enum):
        return self._registry.get(enum)


enum_registry = None


def get_global_enum_registry():
    global enum_registry
    if not enum_registry:
        enum_registry = EnumRegistry()
    return enum_registry