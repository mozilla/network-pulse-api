from rest_framework import serializers

from pulseapi.profiles.models import OrganizationProfile

class OrganizationProfileSerialzer(serializers.ModelSerializer):
    """
    Serializes an Organization Profile
    """
    name = serializers.CharField(

    )

    location = serializers.CharField()

    tagline = serializers.CharField()

    about = serializers.CharField()

    twitter = serializers.URLField()

    linkedin = serializers.URLField()

    email = serializers.EmailField()

    website = serializers.URLField()

    logo = serializers.ImageField()

    administrator = serializers.StringRelatedField()

    issues = serializers.StringRelatedField()

    class Meta:
        model = OrganizationProfile
        # TODO: read_only_fields
        # TODO: exclude fields
