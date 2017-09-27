from rest_framework import serializers

from pulseapi.creators.models import Creator, OrderedCreatorRecord


class CreatorSerializer(serializers.ModelSerializer):
    """
    Serializes creators
    """
    def to_representation(self, obj):
        return obj.name

    class Meta:
        """
        Meta class. Because it's required by ModelSerializer
        """
        model = Creator
        fields = ('name', )


class EntryOrderedCreatorSerializer(serializers.ModelSerializer):
    """
    Serializes creators to be shown in entries where each creator has
    a profile_id if the creator has a user attached to it
    """
    profile_id = serializers.SerializerMethodField()

    def get_profile_id(self, instance):
        user = instance.creator.user

        return user.profile.id if user else None

    # The name of the creator. If the creator is a user, the user's name is
    # used instead
    name = serializers.SerializerMethodField()

    def get_name(self, instance):
        user = instance.creator.user

        return user.profile.name() if user else instance.creator.name

    class Meta:
        model = OrderedCreatorRecord
        fields = ('profile_id', 'name',)
