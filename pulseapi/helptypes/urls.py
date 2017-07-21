from django.conf.urls import url

from pulseapi.helptypes.views import HelpTypeListView

urlpatterns = [
    url('^$', HelpTypeListView.as_view(), name='help-type-list'),
]
