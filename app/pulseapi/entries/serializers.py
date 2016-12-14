"""Serialize the models"""
from rest_framework import serializers

from pulseapi.entries.models import(
    Entry,
)
from pulseapi.tags.models import(
    Tag,
)
from pulseapi.issues.models import(
    Issue,
)

class EntrySerializer(serializers.ModelSerializer):
    """
    Serializes an entry with embeded information including
    list of tags, categories and links associated with that entry
    as simple strings. It also includes a list of hyperlinks to events
    that are associated with this entry as well as hyperlinks to users
    that are involved with the entry
    """
    tags = serializers.SlugRelatedField(many=True, slug_field='name', queryset=Tag.objects)
    issues = serializers.SlugRelatedField(many=True,
                                          slug_field='name',
                                          queryset=Issue.objects)

    class Meta:
        """
        Meta class. Because
        """
        model = Entry
        exclude = ('internal_notes',)
