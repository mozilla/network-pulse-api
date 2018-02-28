"""Serialize the models"""
from rest_framework import serializers
from django.utils.encoding import smart_text
from django.core.exceptions import ObjectDoesNotExist

from pulseapi.entries.models import Entry, ModerationState
from pulseapi.tags.models import Tag
from pulseapi.issues.models import Issue
from pulseapi.helptypes.models import HelpType
from pulseapi.creators.models import Creator, OrderedCreatorRecord
from pulseapi.creators.serializers import EntryOrderedCreatorSerializer


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


class EntrySerializer(EntryBaseSerializer):
    """
    Serializes an entry with embeded information including
    list of tags, categories and links associated with that entry
    as simple strings. It also includes a list of hyperlinks to events
    that are associated with this entry as well as hyperlinks to users
    that are involved with the entry
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

    related_creators = EntryOrderedCreatorSerializer(
        required=False,
        many=True,
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

    def create(self, validated_data):
        """
        We override the create method to make sure we save related creators
        as well and setup the relationship with the created entry.
        """
        related_creators = validated_data.pop('related_creators', [])
        entry = super(EntrySerializer, self).create(validated_data)
        profile = None

        if 'request' in self.context and hasattr(self.context['request'], 'user'):
            profile = self.context['request'].user.profile

        if entry.published_by_creator:
            self_creator, created = Creator.objects.get_or_create(profile=profile)
            if self_creator not in related_creators:
                related_creators.append(self_creator)

        for creator in related_creators:
            creator.save()
            OrderedCreatorRecord.objects.create(
                creator=creator,
                entry=entry,
            )

        return entry

    class Meta:
        """
        Meta class. Because
        """
        model = Entry
        exclude = (
            'internal_notes',
        )
