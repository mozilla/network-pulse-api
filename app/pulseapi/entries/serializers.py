"""Serialize the models"""
from rest_framework import serializers

from pulseapi.entries.models import(
    Entry,
)

class EntrySerializer(serializers.ModelSerializer):
    """
    Serializes an entry with embeded information including
    list of tags, categories and links associated with that entry
    as simple strings. It also includes a list of hyperlinks to events
    that are associated with this entry as well as hyperlinks to users
    that are involved with the entry
    """
    title = serializers.CharField()
    description = serializers.CharField()
    content_url = serializers.URLField()
    thumbnail_url = serializers.URLField()
    tags = serializers.StringRelatedField(many=True)
    issues = serializers.StringRelatedField(many=True)

    class Meta:
        """
        Meta class. Because
        """
        model = Entry
        fields = ("title", "description", "content_url", "thumbnail_url", "tags", "issues",)
