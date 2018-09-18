from rest_framework import serializers

from pulseapi.profiles.models import OrganizationProfile
from pulseapi.issues.models import Issue


class OrganizationProfileSerializer(serializers.ModelSerializer):
    """
    Serializes an entire organization profile
    """
    issues = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Issue.objects.all(),
        required=False,
    )

    class Meta:
        model = OrganizationProfile
        exclude = [
            'administrator',
            'temporary_code',
        ]
