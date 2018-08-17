from rest_framework import serializers

from pulseapi.entries.models import Entry
from pulseapi.issues.models import Issue
from pulseapi.profiles.models import UserProfile


# Helper function to remove a value from a dictionary
# by key, removing the key itself as well.
def remove_key(data, key):
    try:
        del data[key]
    except KeyError:
        pass


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializes a user profile.

    Note that the following fields should only show up when
    the 'enable_extended_information' flag is set to True:

    - user_bio_long
    - program_type
    - program_year
    - affiliation
    """
    profile_id = serializers.ReadOnlyField(source='id')

    custom_name = serializers.CharField(
        max_length=70,
        required=False,
        allow_blank=True,
    )
    location = serializers.CharField(
        max_length=1024,
        required=False,
        allow_blank=True,
    )
    thumbnail = serializers.ImageField(
        required=False,
        allow_null=True,
    )
    issues = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Issue.objects,
        required=False
    )
    twitter = serializers.URLField(
        max_length=2048,
        required=False,
        allow_blank=True,
    )
    linkedin = serializers.URLField(
        max_length=2048,
        required=False,
        allow_blank=True,
    )
    github = serializers.URLField(
        max_length=2048,
        required=False,
        allow_blank=True,
    )
    website = serializers.URLField(
        max_length=2048,
        required=False,
        allow_blank=True,
    )

    user_bio = serializers.CharField(
        max_length=140,
        required=False,
        allow_blank=True,
    )

    is_active = serializers.BooleanField(required=False)

    profile_type = serializers.StringRelatedField()
    program_type = serializers.StringRelatedField()
    program_year = serializers.StringRelatedField()

    entry_count = serializers.SerializerMethodField()

    def get_entry_count(self, obj):
        entry_queryset = Entry.objects.public()

        return {
            'created': obj.related_entry_creators.filter(entry__in=entry_queryset).count(),
            'published': entry_queryset.filter(
                published_by=obj.related_user
            ).count() if getattr(obj, 'related_user', None) else 0,
            'favorited': obj.bookmarks_from.count(),
        }

    @staticmethod
    def trim_extended_information_from_dict(profile, profile_dict):
        if profile and profile.enable_extended_information is False:
            remove_key(profile_dict, 'user_bio_long')
            remove_key(profile_dict, 'program_type')
            remove_key(profile_dict, 'program_year')
            remove_key(profile_dict, 'affiliation')
        # Whether this flag is set or not, it should not
        # end up in the actual serialized profile data.
        remove_key(profile_dict, 'enable_extended_information')
        return profile_dict

    def to_representation(self, instance):
        serialized_profile = super().to_representation(instance)
        return UserProfileSerializer.trim_extended_information_from_dict(
            instance,
            serialized_profile
        )

    def update(self, instance, validated_data):
        validated_data = UserProfileSerializer.trim_extended_information_from_dict(
            instance,
            validated_data
        )
        return super(UserProfileSerializer, self).update(instance, validated_data)

    class Meta:
        """
        Meta class. Because
        """
        model = UserProfile
        read_only_fields = ('profile_type', 'entry_count', 'is_active',)
        exclude = [
            'bookmarks',
            'id',
            'is_group',
        ]
