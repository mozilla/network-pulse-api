from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist

from pulseapi.creators.models import Creator, OrderedCreatorRecord


class CreatorSerializer(serializers.ModelSerializer):
    """
    Serializes creators
    """
    def to_representation(self, instance):
        id = instance.profile.id if instance.profile else False
        return {
          'name': instance.creator_name,
          'creator_id': instance.id,
          'profile_id': id
        }

    class Meta:
        """
        Meta class. Because it's required by ModelSerializer
        """
        model = Creator
        fields = ('name', 'profile',)


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
            'id': creator.id,
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
        has_id = 'id' in data and data['id']
        has_name = 'name' in data and data['name']

        if not has_id and not has_name:
            raise ValidationError(
                detail=_('An id or a name must be provided.'),
                code='missing data',
            )

        if has_id:
            try:
                return Creator.objects.get(id=data['id'])
            except ObjectDoesNotExist:
                raise ValidationError(
                    detail=_('No creator exists for the given id.'),
                    code='invalid',
                )

        return Creator(name=data['name'])

    class Meta:
        model = OrderedCreatorRecord
        fields = '__all__'
