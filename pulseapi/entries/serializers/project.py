from rest_framework import serializers
from .base import EntrySerializerWithCreators


class ProjectEntrySerializer(EntrySerializerWithCreators):

    content_url = serializers.URLField(required=False)
