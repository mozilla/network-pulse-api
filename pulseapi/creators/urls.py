from django.conf.urls import url

from pulseapi.creators.views import (
    CreatorListView,
)


urlpatterns = [
    url('^$', CreatorListView.as_view(), name='creators-list'),
]
