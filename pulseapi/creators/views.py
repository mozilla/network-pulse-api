from django.db.models import Q

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


class FilterCreatorNameBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        search_term = request.query_params.get('name', None)

        if not search_term:
            return queryset

        own_name = Q(name__istartswith=search_term)
        profile_custom = Q(profile__custom_name__istartswith=search_term)
        profile_name = Q(profile__related_user__name__istartswith=search_term)

        return queryset.filter(own_name | profile_custom | profile_name)


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
        FilterCreatorNameBackend,
    )

    search_fields = (
        '^name',
    )
