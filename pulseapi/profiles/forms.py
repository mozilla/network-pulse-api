from django import forms

from pulseapi.creators.models import Creator


class UserProfileAdminForm(forms.ModelForm):
    """
    We use this form for the admin view of a profile so that
    we can add new read-write fields that we want in the admin view
    that aren't present in the model, e.g. reverse-relation fields.
    Any model field that needs to show up in the admin should be defined
    in the fields for the UserProfileAdmin. Only additional non-model
    fields or fields that require custom logic should be defined in this form.
    """
    creator = forms.ModelChoiceField(
        required=False,
        empty_label='(Create one for me)',
        queryset=Creator.objects.all(),
        help_text='The creator associated with this profile.<br />'
                  'NOTE: If you set this to a creator that is already associated with another profile, '
                  'the creator will no longer be attached to that profile and will '
                  'instead be associated with the current profile instead.',
    )

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)

        if instance:
            # We are updating a profile vs. creating a new one
            self.create = False
            kwargs['initial'] = {'creator': instance.related_creator}
        else:
            self.create = True

        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        '''
        Current hack for making sure that we can choose a creator for a profile
        via the admin. Unfortunately, we cannot circumvent the post_save hook
        that automatically creates a Creator for a new profile, so instead,
        we pass along the selected creator to the post_save so that it knows to
        use the selected creator instead of creating a new Creator.
        For updating profiles, the post_save logic isn't triggered and hence,
        we handle the binding of the profile to the selected Creator here, but
        we have to wait for the profile to be saved first to associate it with
        the Creator.
        '''
        instance = super().save(commit=False)
        # Get the chosen creator
        creator = self.cleaned_data['creator']

        # If this is a new profile and a creator was chosen, pass it along
        # to the post_save hook.
        if creator is not None and self.create:
            instance._creator = creator

        instance.save()

        # Handle updating a profile
        if not self.create:
            # Make sure that a different existing creator was set
            if creator is not None and creator.profile != instance:
                # First unbind the creator already related to this profile
                # We use a safe approach here to simply unbind vs. delete the creator
                # So that entries that refer to that creator don't break.
                Creator.objects.filter(pk=instance.related_creator.pk).update(profile=None, name=instance.name)
                # Rebind to the new creator
                creator.profile = instance
                creator.save()
            # Create a new Creator if that was what was chosen
            if creator is None:
                creator = Creator.objects.get_or_create(profile=instance)

        return instance

