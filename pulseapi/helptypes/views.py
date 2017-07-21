"""
Show all issues and a set with descriptions
"""

from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework import filters
from pulseapi.helptypes.serializers import HelpTypeSerializer

from pulseapi.helptypes.models import HelpType

class HelpTypeListView(ListAPIView):
    """
    A view to retrieve all help types.
    """
    queryset = HelpType.objects.all()
    serializer_class = HelpTypeSerializer

    filter_backends = (
        filters.SearchFilter,
    )

    search_fields = (
        '^name',
    )
