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


class EntrySerializer(serializers.ModelSerializer):
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

    # QUEUED FOR DEPRECATION: Use the `related_creators` property instead.
    # See https://github.com/mozilla/network-pulse-api/issues/241
    creators = serializers.SerializerMethodField()

    def get_creators(self, instance):
        """
        Get the list of creators for this entry, which will
        be ordered based on list position at the time the
        entry got posted to Pulse

        (see creators.models.OrderedCreatorRecord Meta class)
        """
        return [ocr.creator.creator_name for ocr in instance.related_creators.all()]

    # QUEUED FOR DEPRECATION: Use the `related_creators` property instead.
    # See https://github.com/mozilla/network-pulse-api/issues/241
    # Although this field has similar results to the field above (it's just
    # serialized differently), we create a new field vs. overriding the field
    # above so that we maintain backward compatibility
    creators_with_profiles = serializers.SerializerMethodField()

    def get_creators_with_profiles(self, instance):
        """
        Get the list of ordered creators with their associated profile info,
        if any, for this entry. Each creator is serialized as:
        {
            "profile_id": <the profile id associated with the creator or null
            if there isn't a profile associated with it>,
            "name": <the name of the creator; uses the profile's name if there
            is a profile>
        }
        """
        return EntryOrderedCreatorSerializer(
            instance.related_creators.all(),
            many=True,
        ).data

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
            res = instance.bookmarked_by.filter(profile=user.profile)
            return res.count() > 0

        return False

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
