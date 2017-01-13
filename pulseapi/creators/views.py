"""
Get creators with filtering for autocomplete purposes
"""

from rest_framework.generics import ListAPIView
from rest_framework import filters
from pulseapi.creators.serializers import (
    CreatorSerializer,
)

from pulseapi.creators.models import Creator

class CreatorListView(ListAPIView):
    """
    A view to retrieve all creators

    Query Params:
    * search - a partial match filter based on the start the tag name
    POST new creators by adding new entries with them
    """
    queryset = Creator.objects.public()
    serializer_class = CreatorSerializer

    filter_backends = (
        filters.SearchFilter,
    )

    search_fields = (
        '^name',
    )
