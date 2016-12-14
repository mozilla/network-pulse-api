"""
Get tags with filtering for autocomplete purposes
"""

from rest_framework.generics import ListAPIView
from rest_framework import filters
from pulseapi.tags.serializers import (
    TagSerializer,
)

from pulseapi.tags.models import Tag

class TagListView(ListAPIView):
    """
    A view to retrieve all tags
    """
    queryset = Tag.objects.public()
    serializer_class = TagSerializer

    filter_backends = (
        filters.SearchFilter,
    )

    search_fields = (
        '^name',
    )
