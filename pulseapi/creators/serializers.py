"""Serialize the models"""
from rest_framework import serializers

from pulseapi.creators.models import(
    Creator,
)

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
