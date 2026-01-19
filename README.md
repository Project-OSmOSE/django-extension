## Use

### settings.py
```python
INSTALLED_APPS = [
    ...,
    "django_extended"
]

REST_FRAMEWORK = {
    ...,
    "DEFAULT_FILTER_BACKENDS": ["django_extended.viewsets.ModelFilter"],
}
```

## Contributor

### Build package

```shell
python -m build
```