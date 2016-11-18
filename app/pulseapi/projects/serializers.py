"""Serialize the models"""
from rest_framework import serializers

from pulseapi.projects.models import(
    Project
)

class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializes a project with embeded information including
    list of tags, categories and links associated with that project
    as simple strings. It also includes a list of hyperlinks to events
    that are associated with this project as well as hyperlinks to users
    that are involved with the project
    """
    title = serializers.CharField()
    description = serializers.CharField()
    content_url = serializers.URLField()
    thumbnail_url = serializers.URLField()
    tags = serializers.CharField()

    class Meta:
        """
        Meta class. Because
        """
        model = Project
        fields = ("title", "description", "content_url", "thumbnail_url", "tags",)
