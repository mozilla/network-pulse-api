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


class UserProfileBasicSerializer(serializers.BaseSerializer):
    """
    A read-only serializer that serializes a user profile by only including indentity
    information like `id` and `name`.
    """
    def to_representation(self, obj):
        return {
            'id': obj.id,
            'name': obj.name,
            'is_active': obj.is_active,
        }


class UserProfileTrimExtendedInfoMixin:
    def trim_extended_information_from_dict(self, profile, profile_dict):
        if profile and profile.enable_extended_information is False:
            remove_key(profile_dict, 'user_bio_long')
            remove_key(profile_dict, 'program_type')
            remove_key(profile_dict, 'program_year')
            remove_key(profile_dict, 'affiliation')
        # Whether this flag is set or not, it should not
        # end up in the actual serialized profile data.
        remove_key(profile_dict, 'enable_extended_information')
        return profile_dict


class UserProfileListSerializer(UserProfileTrimExtendedInfoMixin, serializers.ModelSerializer):
    """
    A serializer to serialize user profiles for optimally viewing
    in a list
    """
    def to_representation(self, instance):
        serialized_profile = super().to_representation(instance)
        return self.trim_extended_information_from_dict(
            instance,
            serialized_profile
        )

    class Meta:
        model = UserProfile
        read_only_fields = fields = (
            'id',
            'name',
            'is_active',
            'is_group',
            'thumbnail',
            'user_bio',
            'user_bio_long',
            'location',
            'affiliation',
            'profile_type',
            'program_type',
            'program_year',
        )


class UserProfileSerializer(UserProfileTrimExtendedInfoMixin, serializers.ModelSerializer):
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

    def to_representation(self, instance):
        serialized_profile = super().to_representation(instance)
        return self.trim_extended_information_from_dict(
            instance,
            serialized_profile
        )

    def update(self, instance, validated_data):
        validated_data = self.trim_extended_information_from_dict(
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
            'created_at',
            'bookmarks',
            'id',
            'is_group',
        ]


class UserProfilePublicSerializer(UserProfileSerializer):
    """
    Serializes a user profile for public view
    """
    name = serializers.CharField(read_only=True)
    my_profile = serializers.SerializerMethodField()

    def get_my_profile(self, instance):
        user = self.context.get('user')
        return user == instance.user
