from django.conf.urls import url

from pulseapi.entries.views import (
    EntriesListView,
    EntryView,
    toggle_bookmark,
    BookmarkedEntries,
)

urlpatterns = [
    url('^$', EntriesListView.as_view(), name='entries-list'),
    url('bookmarks/', BookmarkedEntries.as_view(), name='user-bookmarks'),
    url(r'^(?P<entryid>[0-9]+)/bookmark/?', toggle_bookmark, name='bookmark'),
    url(r'^(?P<pk>[0-9]+)/', EntryView.as_view(), name='entry'),
]
