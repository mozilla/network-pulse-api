"""Serialize the models"""
from rest_framework import serializers

from pulseapi.helptypes.models import HelpType

class HelpTypeSerializer(serializers.ModelSerializer):
    """
    Serializes HelpType
    """
    name = serializers.CharField()
    description = serializers.CharField()

    class Meta:
        """
        Meta class.
        """
        model = HelpType
        fields = ('name', 'description',)
