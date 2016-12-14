from django.conf.urls import url

from pulseapi.tags.views import (
    TagListView,
)


urlpatterns = [
    url('^$', TagListView.as_view(), name='tags-list'),
]
