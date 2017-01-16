from django.conf.urls import url

from pulseapi.entries.views import (
    EntriesListView,
    EntryView,
    toggle_bookmark
)

urlpatterns = [
    url('^$', EntriesListView.as_view(), name='entries-list'),
    url(r'^(?P<entryid>[0-9]+)/bookmark/?', toggle_bookmark, name='bookmark'),
    url(r'^(?P<pk>[0-9]+)/', EntryView.as_view(), name='entry'),
]
