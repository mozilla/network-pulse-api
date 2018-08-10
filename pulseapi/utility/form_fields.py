import uuid
from django.forms import fields, widgets


class TemporaryCheckboxInput(widgets.CheckboxInput):

    template_name = 'widgets/temporary_checkbox.html'

    def value_from_datadict(self, data, files, name):
        value = data.get(name)
        if value is None:
            return value
        try:
            value = uuid.UUID(value)
        except ValueError:
            value = uuid.uuid4()
        return value


class TemporaryField(fields.UUIDField):

    widget = TemporaryCheckboxInput

    def __init__(self, *args, **kwargs):
        kwargs['required'] = False
        super().__init__(*args, **kwargs)
