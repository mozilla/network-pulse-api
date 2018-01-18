from rest_framework import serializers

from pulseapi.issues.models import Issue
from pulseapi.profiles.models import (
    UserProfile,
    UserBookmarks,
)
from pulseapi.creators.models import OrderedCreatorRecord
from pulseapi.entries.serializers import EntrySerializer


class UserBookmarksSerializer(serializers.ModelSerializer):
    """
    Serializes a {user,entry,when} bookmark.
    """

    class Meta:
        """
        Meta class. Again: because
        """
        model = UserBookmarks


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

    def __init__(self , instance , *args , **kwargs ):
        super().__init__(instance , *args , **kwargs)
        if instance.enable_extended_information is False:
            self.fields.pop('user_bio_long')
            self.fields.pop('program_type')
            self.fields.pop('program_year')
            self.fields.pop('affiliation')
        # Whether this flag is set or not, it should not
        # end up in the actual serialized profile data.
        self.fields.pop('enable_extended_information')

    user_bio = serializers.CharField(
        max_length=140,
        required=False,
        allow_blank=True,
    )
    custom_name = serializers.CharField(
        max_length=70,
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

    class Meta:
        """
        Meta class. Because
        """
        model = UserProfile
        exclude = [
            'is_active',
            'bookmarks',
            'id',
            'is_group',
        ]


class UserProfilePublicSerializer(UserProfileSerializer):
    """
    Serializes a user profile for public view
    """
    name = serializers.CharField(read_only=True)

    published_entries = serializers.SerializerMethodField()

    def get_published_entries(self, instance):
        user = instance.user

        return EntrySerializer(
            user.entries.public(),
            context=self.context,
            many=True,
        ).data if user else []

    created_entries = serializers.SerializerMethodField()

    def get_created_entries(self, instance):
        entry_creator_records = OrderedCreatorRecord.objects.filter(creator__profile=instance)
        return [EntrySerializer(x.entry).data for x in entry_creator_records if x.entry.is_approved()]

    my_profile = serializers.SerializerMethodField()

    def get_my_profile(self, instance):
        return self.context.get('request').user == instance.user
