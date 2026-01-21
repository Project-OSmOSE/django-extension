from django.contrib.admin import TabularInline
from django.db.models import Model

from django_extension.models import ExtendedEnum


# class ExtendedTabularInline(TabularInline):
#     enums: {[str]: ExtendedEnum} = None
#     content_types: {[str]: Model} = None
#
#     def formfield_for_dbfield(self, db_field, request, **kwargs):
#         # Todo: for ContactRelationForm
#         return super().formfield_for_dbfield(db_field, request, **kwargs)
