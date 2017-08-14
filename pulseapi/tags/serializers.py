"""Serialize the models"""
from rest_framework import serializers

from pulseapi.tags.models import Tag


class TagSerializer(serializers.ModelSerializer):
    """
    Serializes tags
    """
    def to_representation(self, obj):
        return obj.name

    class Meta:
        """
        Meta class. Because it's required by ModelSerializer
        """
        model = Tag
        fields = ('name', )
