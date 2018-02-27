from rest_framework import serializers
from django.db.models import Prefetch

from pulseapi.issues.models import Issue
from pulseapi.profiles.models import (
    UserProfile,
    UserBookmarks,
)
from pulseapi.creators.models import OrderedCreatorRecord
from pulseapi.entries.models import Entry
from pulseapi.entries.serializers import EntrySerializer


# Helper function to remove a value from a dictionary
# by key, removing the key itself as well.
def remove_key(data, key):
    try:
        del data[key]
    except:
        pass


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

    def __init__(self, instance=None, *args, **kwargs):
        super().__init__(instance, *args, **kwargs)
        if instance is not None and type(instance) is UserProfile:
            # We type-check to prevent this from kicking in for entire
            # QuerySet objects, rather than just UserProfile objects.
            if instance.enable_extended_information is False:
                self.fields.pop('user_bio_long')
                self.fields.pop('program_type')
                self.fields.pop('program_year')
                self.fields.pop('affiliation')
            # Whether this flag is set or not, it should not
            # end up in the actual serialized profile data.
            self.fields.pop('enable_extended_information')

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

    profile_type = serializers.StringRelatedField()
    program_type = serializers.StringRelatedField()
    program_year = serializers.StringRelatedField()

    def update(self, instance, validated_data):
        if instance.enable_extended_information is False:
            remove_key(validated_data, 'user_bio_long')
            remove_key(validated_data, 'program_type')
            remove_key(validated_data, 'program_year')
            remove_key(validated_data, 'affiliation')
        remove_key(validated_data, 'enable_extended_information')
        return super(UserProfileSerializer, self).update(instance, validated_data)

    class Meta:
        """
        Meta class. Because
        """
        model = UserProfile
        read_only_fields = ('profile_type',)
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
    my_profile = serializers.SerializerMethodField()

    def get_my_profile(self, instance):
        return self.context.get('request').user == instance.user


class UserProfilePublicWithEntriesSerializer(UserProfilePublicSerializer):
    """
    Serializes a user profile for public view and includes all entries
    associated with the profile
    """
    published_entries = serializers.SerializerMethodField()

    def get_published_entries(self, instance):
        user = instance.user

        return EntrySerializer(
            user.entries.public().order_by('-id'),
            context=self.context,
            many=True,
        ).data if user else []

    created_entries = serializers.SerializerMethodField()

    def get_created_entries(self, instance):
        entry_creator_records = OrderedCreatorRecord.objects.filter(creator__profile=instance).order_by('-id')
        return [EntrySerializer(x.entry).data for x in entry_creator_records if x.entry.is_approved()]


class UserProfileEntriesSerializer(serializers.Serializer):
    def to_representation(self, instance):
        data = {}
        context = self.context
        include_created = context.get('created', False)
        include_published = context.get('published', False)
        include_favorited = context.get('favorited', False)
        include_all = not (include_created or include_published or include_favorited)

        entries = Entry.objects.public().only(
            'id',
            'title',
            'thumbnail',
            'moderation_state',
            'created',
        )

        if include_created or include_all:
            ordered_creators = OrderedCreatorRecord.objects.filter(creator=instance.related_creator)
            data['created'] = EntrySerializer([
                ordered_creator.entry for ordered_creator in
                ordered_creators.prefetch_related(
                    Prefetch('entry', queryset=entries)
                )
            ], many=True).data

        if include_published or include_all:
            data['published'] = EntrySerializer(
                entries.filter(published_by=instance.user) if instance.user else [],
                many=True
            ).data

        if include_favorited or include_all:
            user_bookmarks = UserBookmarks.objects.filter(profile=instance)
            data['favorited'] = EntrySerializer([
                bookmark.entry for bookmark in
                user_bookmarks.prefetch_related(
                    Prefetch('entry', queryset=entries)
                )
            ], many=True).data

        return data
