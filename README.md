## Use

### settings.py
```python
INSTALLED_APPS = [
    ...,
    "django_extension"
]

REST_FRAMEWORK = {
    ...,
    "DEFAULT_FILTER_BACKENDS": ["django_extension.filters.ModelFilter"],
}
```

## Contributor

### Build package

```shell
python -m build
```