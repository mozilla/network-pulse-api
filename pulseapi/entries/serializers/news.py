from .base import EntrySerializerWithCreators


class NewsEntrySerializer(EntrySerializerWithCreators):

    class Meta(EntrySerializerWithCreators.Meta):
        exclude = EntrySerializerWithCreators.Meta.exclude + (
            'help_types',
        )
