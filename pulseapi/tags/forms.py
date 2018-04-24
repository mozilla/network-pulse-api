from django import forms
from django.contrib.admin import widgets

from pulseapi.entries.models import Entry


class TagAdminForm(forms.ModelForm):
    entries = forms.ModelMultipleChoiceField(
        Entry.objects.all(),
        widget=widgets.FilteredSelectMultiple('Entries', False),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['entries'] = self.instance.entries.values_list('pk', flat=True)
