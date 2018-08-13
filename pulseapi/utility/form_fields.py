import uuid
from django.forms import fields, widgets


class TemporaryCheckboxInput(widgets.CheckboxInput):

    template_name = 'widgets/temporary_checkbox.html'

    def value_from_datadict(self, data, files, name):
        value = data.get(name)
        # If the checkbox was unchecked, the value of the temporary checkbox is None
        if value is None:
            return value

        # Checks if the checkbox was checked and it already had a uuid assigned to it, so that we don't
        # regenerate a new uuid on saving an instance where the checkbox wasn't modified
        try:
            value = uuid.UUID(value)

        # If the checkbox was changed from unchecked to checked, the value will not be an existing uuid (in the
        # current django version the value is on) so we need to generate a new uuid for this input.
        except ValueError:
            value = uuid.uuid4()

        return value


class TemporaryField(fields.UUIDField):

    widget = TemporaryCheckboxInput

    def __init__(self, *args, **kwargs):
        kwargs['required'] = False
        super().__init__(*args, **kwargs)
