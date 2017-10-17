from rest_framework import filters
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination

from pulseapi.creators.serializers import CreatorSerializer
from pulseapi.creators.models import Creator


class CreatorsPagination(PageNumberPagination):
    """
    Add support for pagination and custom page size
    """
    # page size decided in https://github.com/mozilla/network-pulse-api/issues/228
    page_size = 6
    page_size_query_param = 'page_size'
    max_page_size = 20


class CreatorListView(ListAPIView):
    """
    A view that permits a GET to allow listing all creators in the database

    **Route** - `/creators`

    #Query Parameters -

    - ?name= - a partial match filter based on the start of the creator name.

    """
    queryset = Creator.objects.all()
    pagination_class = CreatorsPagination
    serializer_class = CreatorSerializer

    filter_backends = (
        filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    search_fields = (
        '^name',
    )
