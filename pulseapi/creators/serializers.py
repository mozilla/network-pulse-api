from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist

from pulseapi.creators.models import Creator, OrderedCreatorRecord


def serialize_profile_as_v1_creator(profile):
    return {
        'name': profile.name,
        'creator_id': profile.id,  # we include this property only for backwards-compatibility
        'profile_id': profile.id
    }


class CreatorSerializer(serializers.BaseSerializer):
    """
    Read-only serializer that serializes creators (which are actually profile objects)
    This serializer only exists for backwards-compatibility and is disfavored
    over pulseapi.profiles.serializers.UserProfileBasicSerializer
    """
    def to_representation(self, instance):
        return serialize_profile_as_v1_creator(instance)


class EntryCreatorSerializer(serializer.ModelSerializer):
    def to_representation(self, instance):
        pass

    def to_internal_value(self, data):
        pass


class EntryCreatorV1Serializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        return serialize_profile_as_v1_creator(instance.profile)

    def to_internal_value(self, data):



class EntryOrderedCreatorSerializer(serializers.ModelSerializer):
    """
    We use this serializer to serialize creators that are related to entries.
    While the model is set to `OrderedCreatorRecord`, we only do that since we
    inherit from `ModelSerializer`, and the output of serialization/descerialization
    is actually a `Creator` and not an `OrderedCreatorRecord`. We do this because
    for an entry, an `OrderedCreatorRecord` object is not useful while a `Creator`
    object is really what we want.
    """
    def to_representation(self, instance):
        """
        Serialize an `OrderedCreatorRecord` object into something meaningful
        """
        creator = instance.creator

        return {
            'creator_id': creator.id,
            'profile_id': creator.profile.id if creator.profile else None,
            'name': creator.creator_name
        }

    def to_internal_value(self, data):
        """
        Deserialize data passed in into a `Creator` object that can be used to
        create an `OrderedCreatorRecord` object.
        If an `id` is provided, we get the corresponding `Creator` object, otherwise
        we create a new `Creator` object with the name specified but don't actually
        save to the database so that we don't create stale values if something
        fails elsewhere (for e.g. in the `create` method). The `create`/`update`
        methods are responsible for saving this object to the database.
        """
        has_creator_id = 'creator_id' in data and data['creator_id']
        has_name = 'name' in data and data['name']

        if not has_creator_id and not has_name:
            raise ValidationError(
                detail=_('A creator id or a name must be provided.'),
                code='missing data',
            )

        if has_creator_id:
            try:
                return Creator.objects.get(id=data['creator_id'])
            except ObjectDoesNotExist:
                raise ValidationError(
                    detail=_('No creator exists for the given id {id}.'.format(id=data['creator_id'])),
                    code='invalid',
                )

        return Creator(name=data['name'])

    class Meta:
        model = OrderedCreatorRecord
        fields = '__all__'
