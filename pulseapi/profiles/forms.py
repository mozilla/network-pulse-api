from django import forms


class ProfileAdminForm(forms.ModelForm):

    def clean_thumbnail(self):
        data = self.cleaned_data["thumbnail"]
        if not data:
            return data
        if data.size > 512*1024:
            raise forms.ValidationError("Image size must be less than 500KB")
        return data
