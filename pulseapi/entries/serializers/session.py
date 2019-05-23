from rest_framework import serializers
from .base import EntrySerializerWithCreators


class SessionEntrySerializer(EntrySerializerWithCreators):

    content_url = serializers.URLField(required=False)

    class Meta(EntrySerializerWithCreators.Meta):
        exclude = EntrySerializerWithCreators.Meta.exclude + (
            'thumbnail',
            'get_involved',
            'get_involved_url',
        )
