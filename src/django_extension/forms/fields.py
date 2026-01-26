from typing import Type

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import Choices, Model

from .widgets import AdminAutocompleteSelectWidget

__all__ = [
    'EnumAutocompleteSelectField',
    'ContentTypeAutocompleteSelectField'
]


class EnumAutocompleteSelectField(forms.ChoiceField):

    def __init__(self, *, enum: Type[Choices], **kwargs):
        super().__init__(choices=enum.choices, widget=AdminAutocompleteSelectWidget(choices=enum.choices), **kwargs)


class ContentTypeAutocompleteSelectField(forms.ChoiceField):

    def __init__(self, *,
                 models: [Type[Model]],
                 **kwargs):
        choices = [("-", "---")] + [
            (
                f"{m._meta.app_label}.{m._meta.model_name}--{o.pk}",  # Value
                f"{m.__name__}: {str(o)}"  # Label
            )
            for m in models
            for o in m.objects.all()
        ]
        super().__init__(choices=choices, widget=AdminAutocompleteSelectWidget(choices=choices), **kwargs)

    def prepare_value(self, value):
        if value is None or value == "-":
            return None
        return f"{value._meta.app_label}.{value._meta.model_name}--{value.pk}"

    def clean(self, value):
        is_none = False
        if value == '-':
            value = None
            is_none = True
        value = super().clean(value)
        if is_none:
            # Return after clean to allow common behavior on required fields
            return None
        ct, pk = value.split('--')
        app, model = ct.split('.')
        return ContentType.objects.get(
            app_label=app,
            model=model
        ).model_class().objects.get(pk=pk)
