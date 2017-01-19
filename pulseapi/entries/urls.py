from django.conf.urls import url

from pulseapi.entries.views import (
    EntriesListView,
    EntryView,
    toggle_bookmark,
    FavoriteEntries,
)

urlpatterns = [
    url('^$', EntriesListView.as_view(), name='entries-list'),
    url('favorites/', FavoriteEntries.as_view(), name='user-favorites'),
    url(r'^(?P<entryid>[0-9]+)/bookmark/?', toggle_bookmark, name='bookmark'),
    url(r'^(?P<pk>[0-9]+)/', EntryView.as_view(), name='entry'),
]
