"""Serialize the models"""
from rest_framework import serializers
from django.utils.encoding import smart_text
from django.core.exceptions import ObjectDoesNotExist

from pulseapi.entries.models import Entry, ModerationState
from pulseapi.tags.models import Tag
from pulseapi.issues.models import Issue
from pulseapi.helptypes.models import HelpType
from pulseapi.creators.models import EntryCreator
from pulseapi.creators.serializers import (
    RelatedEntryCreatorV1Field,
    RelatedEntryCreatorField,
)


def associate_entry_with_creator_data(entry, creator_data=[], user=None):
    if user and entry.published_by_creator:
        creator_data.append({'profile': user.profile})

    for data in creator_data:
        if not data.pop('profile_committed', True):
            data.profile.save()
        EntryCreator.objects.create(entry=entry, **data)


class CreatableSlugRelatedField(serializers.SlugRelatedField):
    """
    Override SlugRelatedField to create or update
    instead of getting upset that a tag doesn't exist
    """
    def to_internal_value(self, data):
        try:
            qs = self.get_queryset()
            return qs.get_or_create(**{self.slug_field: data})[0]
        except ObjectDoesNotExist:
            self.fail(
                'does_not_exist',
                slug_name=self.slug_field,
                value=smart_text(data)
            )
        except (TypeError, ValueError):
            self.fail('invalid')


class ModerationStateSerializer(serializers.ModelSerializer):
    class Meta:
        """
        Meta class. Because
        """
        model = ModerationState
        exclude = ()


class EntryBaseSerializer(serializers.ModelSerializer):
    """
    Serializes an entry with minimal information
    """

    is_bookmarked = serializers.SerializerMethodField()

    def get_is_bookmarked(self, instance):
        """
        Check whether the current user has bookmarked this
        Entry. Anonymous users always see False
        """
        user = None
        if 'request' in self.context and hasattr(self.context['request'], 'user'):
            user = self.context['request'].user

        if user and user.is_authenticated():
            # instance.bookmarked_by.all() is already prefetched and cached in the QuerySet
            return any(bookmark_by.profile.user == user for bookmark_by in instance.bookmarked_by.all())

        return False

    class Meta:
        model = Entry
        read_only_fields = fields = (
            'title',
            'content_url',
            'thumbnail',
            'is_bookmarked',
        )


class EntryWithV1CreatorsBaseSerializer(EntryBaseSerializer):
    related_creators = RelatedEntryCreatorV1Field(
        queryset=EntryCreator.objects.all(),
        source='related_entry_creators',
        required=False,
        many=True,
    )

    class Meta(EntryBaseSerializer.Meta):
        read_only_fields = fields = EntryBaseSerializer.Meta.fields + ('related_creators',)


class EntryWithCreatorsBaseSerializer(EntryBaseSerializer):
    related_creators = RelatedEntryCreatorField(
        queryset=EntryCreator.objects.all(),
        source='related_entry_creators',
        required=False,
        many=True,
    )

    class Meta(EntryBaseSerializer.Meta):
        read_only_fields = fields = EntryBaseSerializer.Meta.fields + ('related_creators',)


class EntrySerializer(EntryBaseSerializer):
    """
    Serializes an entry with embeded information including
    list of tags, issues and help types associated with that entry
    as simple strings.
    """

    tags = CreatableSlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Tag.objects,
        required=False
    )

    issues = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Issue.objects,
        required=False
    )

    help_types = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=HelpType.objects,
        required=False
    )

    # overrides 'published_by' for REST purposes
    # as we don't want to expose any user's email address
    published_by = serializers.SlugRelatedField(
        source='published_by.profile',
        slug_field='name',
        read_only=True,
    )

    # "virtual" property so that we can link to the correct profile
    submitter_profile_id = serializers.SlugRelatedField(
        source='published_by.profile',
        slug_field='id',
        read_only=True,
    )

    bookmark_count = serializers.SerializerMethodField()

    def get_bookmark_count(self, instance):
        """
        Get the total number of bookmarks this entry received
        """
        return instance.bookmarked_by.count()

    class Meta:
        """
        Meta class. Because
        """
        model = Entry
        exclude = (
            'internal_notes',
        )


class EntrySerializerWithCreators(EntrySerializer):
    related_creators = RelatedEntryCreatorField(
        queryset=EntryCreator.objects.all(),
        source='related_entry_creators',
        required=False,
        many=True,
    )

    def create(self, validated_data):
        """
        We override the create method to make sure we save related creators
        as well and setup the relationship with the created entry.
        """
        user = self.context.get('user')
        creator_data = validated_data.pop('related_creators', [])
        entry = super().create(validated_data)

        if user and entry.published_by_creator:
            creator_data.append({'profile': user.profile})

        for data in creator_data:
            if not data.pop('profile_committed', True):
                data.profile.save()
            EntryCreator.objects.create(entry=entry, **data)

        return entry


class EntrySerializerWithV1Creators(EntrySerializerWithCreators):
    related_creators = RelatedEntryCreatorV1Field(
        queryset=EntryCreator.objects.all(),
        source='related_entry_creators',
        required=False,
        many=True,
    )
