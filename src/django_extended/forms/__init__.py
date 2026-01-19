from django import forms
from django.contrib.contenttypes.models import ContentType
from django.forms.utils import ErrorList

__all__ = [
    'ExtendedForm'
]

class ExtendedForm(forms.ModelForm):
    pass



class ContentTypeModelForm(forms.ModelForm):

    # Metaclass should include:
    #  - content_type_field_name: str
    #  - object_id_field_name: str
    #  - object_field_name: str

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None, renderer=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance,
                         use_required_attribute, renderer)
        object = getattr(self.instance, self.Meta.object_field_name)
        self.initial[self.Meta.object_field_name] = f"{object._meta.app_label}.{object._meta.model_name}--{object.pk}"
        print(self.initial, self.Meta)

    def _post_clean(self):
        super()._post_clean()
        model, pk = self.cleaned_data[self.Meta.object_field_name].split('--')
        app_label, model_name = model.split('.')
        ct = ContentType.objects.get(app_label=app_label, model=model_name)
        setattr(self.instance, self.Meta.content_type_field_name, ct)
        setattr(self.instance, self.Meta.object_id_field_name, pk)
        setattr(self.instance, self.Meta.object_field_name, ct.get_object_for_this_type(pk=pk))
