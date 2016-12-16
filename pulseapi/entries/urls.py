from django.conf.urls import url

from pulseapi.entries.views import (
    EntriesListView,
    EntryView,
)


urlpatterns = [
    url('^$', EntriesListView.as_view(), name='entries-list'),
    url(r'^(?P<pk>[0-9]+)/', EntryView.as_view(), name='entry'),
]
