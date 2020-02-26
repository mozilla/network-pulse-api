from .base import EntrySerializerWithCreators


class NewsEntrySerializer(EntrySerializerWithCreators):
    help_types = None

    class Meta(EntrySerializerWithCreators.Meta):
        exclude = EntrySerializerWithCreators.Meta.exclude + (
            'help_types',
        )
