from django.db import models
from . import form_fields


class TemporaryField(models.UUIDField):

    description = 'A unique identifier for a temporary instance'

    def __init__(self, *args, **kwargs):
        kwargs['verbose_name'] = None
        kwargs['null'] = True
        kwargs['unique'] = True
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['verbose_name']
        del kwargs['null']
        del kwargs['unique']
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        return super().formfield(**{
            'form_class': form_fields.TemporaryField,
            **kwargs,
        })
