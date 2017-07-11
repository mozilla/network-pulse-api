"""Serialize the models"""
from rest_framework import serializers

from pulseapi.issues.models import(
    Issue,
)

class IssueSerializer(serializers.ModelSerializer):
    """
    Serializes Issues
    """
    name = serializers.CharField()
    description = serializers.CharField()

    class Meta:
        """
        Meta class. Because it's required by ModelSerializer
        """
        model = Issue
        fields = ('name', 'description',)

class IssueDetailSerializer(serializers.ModelSerializer):
    """
    Serializes Issues
    """
    name = serializers.CharField()
    description = serializers.CharField()

    class Meta:
        """
        Meta class. Because it's required by ModelSerializer
        """
        model = Issue
        fields = ('name', 'description',)
