from rest_framework import serializers

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
    Serializes creators to be shown in entries where each creator has
    a profile_id if the creator has a user attached to it
    """
    profile_id = serializers.SerializerMethodField()

    def get_profile_id(self, instance):
        profile = instance.creator.profile

        return profile.id if profile else None

    # The name of the creator. If the creator is a user, the user's name is
    # used instead
    name = serializers.SlugRelatedField(
        source='creator',
        slug_field='creator_name',
        read_only=True,
    )

    class Meta:
        model = OrderedCreatorRecord
        fields = ('profile_id', 'name',)
