from rest_framework import serializers

from pulseapi.creators.models import EntryCreator
from pulseapi.entries.serializers import EntrySerializerWithV1Creators
from .public import UserProfilePublicSerializer


class UserProfilePublicWithEntriesSerializer(UserProfilePublicSerializer):
    """
    Serializes a user profile for public view and includes all entries
    associated with the profile
    """
    published_entries = serializers.SerializerMethodField()

    def get_published_entries(self, instance):
        user = instance.user

        return EntrySerializerWithV1Creators(
            user.entries.public().with_related().order_by('-id'),
            many=True,
            context={'user': self.context.get('user')}
        ).data if user else []

    created_entries = serializers.SerializerMethodField()

    def get_created_entries(self, instance):
        entry_creators = EntryCreator.objects.filter(profile=instance).order_by('-id')
        return [EntrySerializerWithV1Creators(x.entry).data for x in entry_creators if x.entry.is_approved()]
