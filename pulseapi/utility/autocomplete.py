from django.core.exceptions import FieldDoesNotExist
from ajax_select.registry import registry
from ajax_select.fields import AutoCompleteSelectMultipleField, AutoCompleteSelectField


def autoselect_fields_check_can_add(form, model, user):
    """
    Adapted from ajax_select.fields from the django-ajax-selects package.
    Modified to catch non-database fields and use the lookup to determine
    if the user has the add permission for that lookup's model.
    """
    for name, form_field in form.declared_fields.items():
        if isinstance(form_field, (AutoCompleteSelectMultipleField, AutoCompleteSelectField)):
            try:
                db_field = model._meta.get_field(name)
                if hasattr(db_field, "remote_field"):
                    form_field.check_can_add(user, db_field.remote_field.model)
                else:
                    form_field.check_can_add(user, db_field.rel.to)
            except FieldDoesNotExist:
                lookup = registry.get(form_field.channel)
                form_field.check_can_add(user, lookup.model)
