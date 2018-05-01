from django import forms
from ajax_select.fields import AutoCompleteSelectMultipleField

from pulseapi.creators.models import EntryCreator


class EntryAdminForm(forms.ModelForm):
    creators = AutoCompleteSelectMultipleField(
        'profiles',
        plugin_options={
            'minLength': 3,
        },
        widget_options={
            'attrs': {
                'placeholder': 'Enter a creator\'s name to add to the list'
            }
        },
        help_text='',  # We do this since the default django help text isn't positioned correctly with our custom CSS
    )

    bookmark_count = forms.IntegerField(disabled=True, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['creators'] = self.instance.related_entry_creators.values_list('profile__pk', flat=True)
            self.initial['bookmark_count'] = self.instance.bookmarked_by.count()

        if not self.current_user.has_perm('entries.change_creators'):
            self.fields['creators'].disabled = True

    def _save_m2m(self):
        super()._save_m2m()

        entry = self.instance
        creator_profile_id_list = self.cleaned_data['creators']
        entry.related_entry_creators.all().delete()

        for creator_profile_id in creator_profile_id_list:
            profile_id = int(creator_profile_id)
            EntryCreator.objects.create(entry=entry, profile_id=profile_id)
