from itertools import chain
from django.db.models import Q
from django.conf import settings
from rest_framework import filters
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import exceptions

from pulseapi.profiles.models import UserProfile
from pulseapi.creators.serializers import CreatorSerializer


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

        profile_custom = Q(custom_name__istartswith=search_term)
        profile_name = Q(related_user__name__istartswith=search_term)
        istartswith_filter = profile_custom | profile_name
        qs = queryset.filter(istartswith_filter)

        # If the number of results returned is less than the allowed
        # page_size, we can instead rerun this using `contains` rules,
        # rather than using the `startswith` rule.
        page_size_query = request.query_params.get('page_size', None)
        page_size = int(page_size_query if page_size_query else CreatorsPagination.page_size)
        flen = len(qs)

        if flen < page_size:
            profile_custom = Q(custom_name__icontains=search_term)
            profile_name = Q(related_user__name__icontains=search_term)
            icontains_filter = profile_custom | profile_name
            icontains_qs = queryset.filter(icontains_filter).exclude(istartswith_filter)
            # make sure we keep our exact matches at the top of the result list
            qs = list(chain(qs, icontains_qs))

        return qs


class CreatorListView(ListAPIView):
    """
    A view that permits a GET to allow listing all creators in the database

    Note
    ----
    This view only exists for backwards-compatibility (version 1). Creators no longer exist as independent models
    and hence the pulseapi.profiles.views.UserProfileListAPIView should be used instead.

    **Route** - `/creators`

    #Query Parameters -

    - ?name= - a partial match filter based on the start of the creator name.

    """
    queryset = UserProfile.objects.all()
    pagination_class = CreatorsPagination
    serializer_class = CreatorSerializer

    filter_backends = (
        filters.DjangoFilterBackend,
        FilterCreatorNameBackend,
    )

    search_fields = (
        '^name',
    )

    def get(self, request, *args, **kwargs):
        if request.version == settings.API_VERSIONS['version_1']:
            return super().get(request, *args, **kwargs)

        raise exceptions.NotFound(
            'The {path} route has been deprecated and is no longer supported in version {version}'.format(
                path=request.path,
                version=request.version
            )
        )
