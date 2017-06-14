from django.conf.urls import url

from pulseapi.entries.views import (
    toggle_bookmark,
    toggle_moderation,
    EntryView,
    BookmarkedEntries,
    ModerationStateView,
    EntriesListView,
)

urlpatterns = [
    url(
    	'^$',
    	EntriesListView.as_view(),
    	name='entries-list'
    ),
    url(
    	'bookmarks/',
    	BookmarkedEntries.as_view(),
    	name='user-bookmarks'
    ),
    url(
    	r'^(?P<entryid>[0-9]+)/bookmark/?',
    	toggle_bookmark,
    	name='bookmark'
    ),
    url(
        r'^(?P<entryid>[0-9]+)/moderate/(?P<stateid>[0-9]+)/?',
        toggle_moderation,
        name='moderate'
    ),
    url(
    	r'^(?P<pk>[0-9]+)/',
    	EntryView.as_view(),
    	name='entry'
    ),
    url(
        'moderation-states/',
        ModerationStateView.as_view(),
        name='moderation-states'
    )
]
