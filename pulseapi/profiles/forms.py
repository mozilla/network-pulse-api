from django import forms

from pulseapi.utility.image_validation import enforce_image_size_limit


class ProfileAdminForm(forms.ModelForm):

    def clean_thumbnail(self):
        data = self.cleaned_data["thumbnail"]
        return enforce_image_size_limit(data)
