from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist

from pulseapi.profiles.models import UserProfile
from pulseapi.entries.models import Entry


def serialize_profile_as_creator(profile):
    return {
        'name': profile.name,
        'profile_id': profile.id
    }


def serialize_profile_as_v1_creator(profile):
    serialized_profile = serialize_profile_as_creator(profile)
    serialized_profile['creator_id'] = profile.id  # we include this property only for backwards-compatibility
    return serialized_profile


def get_or_create_userprofile(data, id_key):
    """
    Deserialize data into a `UserProfile` object.
    The `data` is checked for a value corresponding to the id_key.
    If it exists, we get the corresponding `UserProfile` object, otherwise
    we create a new `UserProfile` object with the name specified.
    We don't save the instance to the database and that is left to
    the calling function to save the instance.

    Returns a dictionary with two keys - `object` and `created`,
    where `object` is the retrieved or created `UserProfile` instance and
    `created` is a boolean specifying whether a new instance was created
    """
    profile_id = data.get(id_key)
    name = data.get('name')

    if not profile_id and not name:
        raise ValidationError(
            detail=_('A creator/profile id or a name must be provided.'),
            code='missing data',
        )

    if profile_id:
        try:
            return UserProfile.objects.get(id=profile_id), False
        except ObjectDoesNotExist:
            raise ValidationError(
                detail=_('No profile exists for the given id {id}.'.format(id=profile_id)),
                code='invalid',
            )

    return UserProfile(custom_name=name), True


def get_entry(data):
    entry_id = data.get('entry_id')
    if not entry_id:
        return None

    try:
        return Entry.objects.get(id=entry_id)
    except ObjectDoesNotExist:
        raise ValidationError(
            detail=_('No entry exists for the given id {id}.'.format(id=entry_id)),
            code='invalid',
        )


def deserialize_entry_creator(data, profile_id_key):
    profile, created = get_or_create_userprofile(data, profile_id_key)
    entry = get_entry(data)

    entry_creator_data = {
        'profile': profile,
        'profile_committed': not created
    }
    if entry:
        entry_creator_data['entry'] = entry

    return entry_creator_data


class CreatorSerializer(serializers.BaseSerializer):
    """
    Read-only serializer that serializes creators (which are actually profile objects)
    This serializer only exists for backwards-compatibility and is disfavored
    over pulseapi.profiles.serializers.UserProfileBasicSerializer
    """
    def to_representation(self, instance):
        return serialize_profile_as_v1_creator(instance)


class RelatedEntryCreatorField(serializers.RelatedField):
    def to_representation(self, instance):
        return serialize_profile_as_creator(instance.profile)

    def to_internal_value(self, data):
        """
        Returns a dictionary:
        {
            'profile': deserialized instance of `UserProfile`
            'profile_committed': boolean indicating whether the profile
            instance is from the database or needs to be committed
        }
        This dictionary will also contain an `entry` if a valid `entry_id`
        was passed in with the `data`

        Expects either a `profile_id` or a `name` to exist in the `data`.
        """
        return deserialize_entry_creator(data, 'profile_id')


class RelatedEntryCreatorV1Field(serializers.RelatedField):
    def to_representation(self, instance):
        return serialize_profile_as_v1_creator(instance.profile)

    def to_internal_value(self, data):
        """
        Returns a dictionary:
        {
            'profile': deserialized instance of `UserProfile`
            'profile_committed': boolean indicating whether the profile
            instance is from the database or needs to be committed
        }
        This dictionary will also contain an `entry` if a valid `entry_id`
        was passed in with the `data`

        Expects either a `creator_id` or a `name` to exist in the `data`.
        """
        return deserialize_entry_creator(data, 'creator_id')
