from django.conf.urls import url

from pulseapi.issues.views import (
    IssueListView,
    IssueDetailView,
)


urlpatterns = [
    url('^$', IssueListView.as_view(), name='issue-list'),
    url(r'^(?P<name>[\w\s\&]+)/', IssueDetailView.as_view(), name='issue-detail'),
]
