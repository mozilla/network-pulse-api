"""
Views to get entries
"""

import django_filters
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters

from pulseapi.entries.models import Entry
from pulseapi.entries.serializers import (
    EntrySerializer,
)


class EntryCustomFilter(filters.FilterSet):
    """
    We add custom filtering to allow you to filter by:
        * Tag - pass the `?tag=` query parameter
        * Issue - pass the `?issue=` query parameter
    Accepts only one filter value i.e. one tag and/or one
    category.
    """
    tag = django_filters.CharFilter(
        name='tags__name',
        lookup_expr='iexact',
    )
    issue = django_filters.CharFilter(
        name='issues__name',
        lookup_expr='iexact',
    )

    class Meta:
        """
        Required Meta class
        """
        model = Entry
        fields = ['tags', 'issues',]

class EntryView(RetrieveAPIView):
    """
    A view to retrieve individual entries
    """
    queryset = Entry.objects.public()
    serializer_class = EntrySerializer
    pagination_class = None

class EntriesListView(ListCreateAPIView):
    """
    A view that permits a GET to allow listing all the entries
    in the database

    **Route** - `/entries`

    **Query Parameters** -

    - `?search=` - Allows search terms
    - `?tag=` - Allows filtering entries by a specific tag
    - `?issue=` - Allows filtering entries by a specific issue
    """
    queryset = Entry.objects.public()
    pagination_class = PageNumberPagination
    filter_backends = (
        filters.DjangoFilterBackend,
        filters.SearchFilter,
    )
    filter_class = EntryCustomFilter
    search_fields = (
        'title',
        'description',
    )
    serializer_class = EntrySerializer
