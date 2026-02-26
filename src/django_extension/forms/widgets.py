from django import forms
from django.contrib.admin.widgets import AutocompleteMixin

__all__ = [
    'AdminAutocompleteSelectWidget',
    'AdminAutocompleteSelectMultipleWidget',
]

from django.utils.safestring import mark_safe


# Base Source - https://stackoverflow.com/a/79216626
# Posted by rptmat57
# Retrieved 2025-12-03, License - CC BY-SA 4.0
class AdminAutocompleteSelectWidget(forms.Select):
    url_name = '%s:autocomplete'

    def __init__(self, choices=(), attrs=None):
        super().__init__(attrs=attrs)
        self.choices = choices
        self.base_mixin = AutocompleteMixin(None, None)

    def build_attrs(self, base_attrs, extra_attrs=None):
        """
        Set select2's AJAX attributes.

        Attributes can be set using the html5 data attribute.
        Nested attributes require a double dash as per
        https://select2.org/configuration/data-attributes#nested-subkey-options
        """
        attrs = super().build_attrs(base_attrs, extra_attrs=extra_attrs)
        attrs.setdefault('class', '')
        attrs.update({
            'data-theme': 'admin-autocomplete',
            'data-placeholder': '',  # Allows clearing of the input.
            'class': attrs['class'] + (' ' if attrs['class'] else '') + 'admin-autocomplete',
        })
        return attrs

    def render(self, name, value, attrs=None, renderer=None):
        select_html = super().render(name, value, attrs, renderer)
        select2_script = f"""
        <script type="text/javascript">
            (function($) {{
                $(document).ready(function() {{
                    $('#id_{name}').select2();
                }});
            }})(django.jQuery);
        </script>
        """
        return mark_safe(select_html + select2_script)

    @property
    def media(self):
        # Reuse the AutocompleteMixin's media files
        return self.base_mixin.media

class AdminAutocompleteSelectMultipleWidget(forms.SelectMultiple):
    url_name = '%s:autocomplete'

    def __init__(self, choices=(), attrs=None):
        super().__init__(attrs=attrs)
        self.choices = choices
        self.base_mixin = AutocompleteMixin(None, None)

    def build_attrs(self, base_attrs, extra_attrs=None):
        """
        Set select2's AJAX attributes.

        Attributes can be set using the html5 data attribute.
        Nested attributes require a double dash as per
        https://select2.org/configuration/data-attributes#nested-subkey-options
        """
        attrs = super().build_attrs(base_attrs, extra_attrs=extra_attrs)
        attrs.setdefault('class', '')
        attrs.update({
            'data-theme': 'admin-autocomplete',
            'data-placeholder': '',  # Allows clearing of the input.
            'class': attrs['class'] + (' ' if attrs['class'] else '') + 'admin-autocomplete',
        })
        return attrs

    def render(self, name, value, attrs=None, renderer=None):
        select_html = super().render(name, value, attrs, renderer)
        select2_script = f"""
        <script type="text/javascript">
            (function($) {{
                $(document).ready(function() {{
                    $('#id_{name}').select2();
                }});
            }})(django.jQuery);
        </script>
        """
        return mark_safe(select_html + select2_script)

    @property
    def media(self):
        # Reuse the AutocompleteMixin's media files
        return self.base_mixin.media
