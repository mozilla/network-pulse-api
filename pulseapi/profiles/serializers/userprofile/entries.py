from django.db.models import Q, Prefetch
from rest_framework import serializers

from pulseapi.creators.models import EntryCreator
from pulseapi.entries.models import Entry
from pulseapi.profiles.models import UserBookmarks
from pulseapi.entries.serializers import EntryWithCreatorsBaseSerializer


class UserProfileEntriesSerializer(serializers.Serializer):
    """
    Serializes entries related to a profile based on the requested
    entry types.

    Add any combination of the following parameters to the serializer context
    to request specific types of entries in the serialized data:
    - `created` - List of entries created by the profile
    - `published` - List of entries published by the profile
    - `favorited` - List of entries favorited/bookmarked by the profile

    If none of these parameters are passed in, this serializer falls back to
    returning the number of entries (created, published, and favorited) associated
    with the profile.
    """
    @staticmethod
    def get_ordered_queryset(queryset, ordering_param=None, prefix=False):
        if not ordering_param:
            return queryset

        if prefix:
            if ordering_param[0] is '-':
                ordering_param = '-' + prefix + ordering_param[1:]
            else:
                ordering_param = prefix + ordering_param

        return queryset.order_by(ordering_param)

    def to_representation(self, instance):
        data = {}
        context = self.context
        user = context.get('user')
        include_created = context.get('created', False)
        include_published = context.get('published', False)
        include_favorited = context.get('favorited', False)
        created_ordering = context.get('created_ordering', False)
        published_ordering = context.get('published_ordering', False)
        favorited_ordering = context.get('favorited_ordering', False)
        EntrySerializerClass = context.get('EntrySerializerClass', EntryWithCreatorsBaseSerializer)

        # If none of the filter options are provided, only return the count of
        # entries associated with this profile
        if not (include_created or include_published or include_favorited):
            entry_count = Entry.objects.public().filter(
                Q(related_entry_creators__profile=instance) |
                Q(published_by=instance.user) |
                Q(bookmarked_by__profile=instance)
            ).distinct().count()
            return {
                'entry_count': entry_count
            }

        entry_queryset = Entry.objects.prefetch_related(
            'related_entry_creators__profile__related_user',
            'bookmarked_by__profile__related_user',
        )

        if include_created:
            entry_creators = UserProfileEntriesSerializer.get_ordered_queryset(
                queryset=(
                    EntryCreator.objects
                    .prefetch_related(Prefetch('entry', queryset=entry_queryset))
                    .filter(profile=instance)
                    .filter(entry__in=Entry.objects.public())
                ),
                ordering_param=created_ordering,
                prefix='entry__',
            )
            data['created'] = [
                EntrySerializerClass(
                    entry_creator.entry,
                    context={'user': user}
                ).data
                for entry_creator in entry_creators
            ]

        if include_published:
            if instance.user:
                entries = UserProfileEntriesSerializer.get_ordered_queryset(
                    queryset=entry_queryset.public().filter(published_by=instance.user),
                    ordering_param=published_ordering,
                )
            else:
                entries = []

            data['published'] = EntrySerializerClass(
                entries,
                context={'user': user},
                many=True
            ).data

        if include_favorited:
            user_bookmarks = UserProfileEntriesSerializer.get_ordered_queryset(
                queryset=(
                    UserBookmarks.objects.filter(profile=instance)
                    .filter(entry__in=Entry.objects.public())
                    .prefetch_related(Prefetch('entry', queryset=entry_queryset))
                ),
                ordering_param=favorited_ordering,
                prefix='entry__',
            )
            data['favorited'] = [
                EntrySerializerClass(bookmark.entry, context={'user': user}).data for bookmark in user_bookmarks
            ]

        return data
