from django import forms


def enforce_image_size_limit(data):
    if data and data.size > 512 * 1024:
        raise forms.ValidationError("Image size must be less than 500KB")
    return data
