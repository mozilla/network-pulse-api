"""
Show all issues and a set with descriptions
"""

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework import filters
from pulseapi.issues.serializers import (
    IssueSerializer,
    IssueDetailSerializer,
)

from pulseapi.issues.models import Issue

class IssueListView(ListAPIView):
    """
    A view to retrieve all Issues
    """
    queryset = Issue.objects.public()
    serializer_class = IssueSerializer

    filter_backends = (
        filters.SearchFilter,
    )

    search_fields = (
        '^name',
    )

class IssueDetailView(RetrieveAPIView):
    """
    A view to give the description (and potentially future details) of an issue
    """
    pagination_class = None
    serializer_class = IssueDetailSerializer
    lookup_field = 'name'

    def get_queryset(self):
        return Issue.objects.public().slug(self.kwargs['name'])
