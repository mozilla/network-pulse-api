import base64
from itertools import chain
import django_filters

from django.core.files.base import ContentFile
from django.conf import settings
from django.db.models import Q

from django_filters.rest_framework import (
    DjangoFilterBackend,
    FilterSet,
)

from rest_framework import permissions
from rest_framework.filters import (
    SearchFilter,
    OrderingFilter
)
from rest_framework.generics import (
    RetrieveUpdateAPIView,
    RetrieveAPIView,
    ListAPIView,
    get_object_or_404,
)
from rest_framework.pagination import PageNumberPagination

from pulseapi.profiles.models import UserProfile
from pulseapi.profiles.serializers import (
    UserProfileSerializer,
    UserProfilePublicWithEntriesSerializer,
    UserProfilePublicSerializer,
    UserProfileBasicSerializer,
    UserProfileListSerializer,
)


class IsProfileOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class UserProfileAPIView(RetrieveUpdateAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsProfileOwner
    )

    serializer_class = UserProfileSerializer

    def get_object(self):
        user = self.request.user
        return get_object_or_404(
            UserProfile.objects.prefetch_related(
                'issues',
                'related_user',
                'bookmarks_from',
            ),
            related_user=user
        )

    def get_serializer_context(self):
        return {
            'user': self.request.user
        }

    def put(self, request, *args, **kwargs):
        """
        If there is a thumbnail, and it was sent as part of an
        application/json payload, then we need to unpack a thumbnail
        object payload and convert it to a Python ContentFile payload
        instead. We use a try/catch because the optional nature means
        we need to check using "if hasattr(request.data,'thumbnail'):"
        as we as "if request.data['thumbnail']" and these are pretty
        much mutually exclusive patterns. A try/pass make far more sense.
        """

        payload = request.data
        thumbnail = payload.get('thumbnail')

        if thumbnail:
            name = thumbnail.get('name')
            encdata = thumbnail.get('base64')
            if name and encdata:
                request.data['thumbnail'] = ContentFile(
                    base64.b64decode(encdata),
                    name=name,
                )

        return super(UserProfileAPIView, self).put(request, *args, **kwargs)


class UserProfilePublicAPIView(RetrieveAPIView):
    queryset = UserProfile.objects.all()

    def get_serializer_class(self):
        if self.request.version == settings.API_VERSIONS['version_1']:
            return UserProfilePublicWithEntriesSerializer

        return UserProfilePublicSerializer

    def get_serializer_context(self):
        return {
            'user': self.request.user
        }


class UserProfilePublicSelfAPIView(UserProfilePublicAPIView):
    def get_object(self):
        user = self.request.user
        return get_object_or_404(self.queryset, related_user=user)


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


class ProfileCustomFilter(FilterSet):
    """
      We add custom filtering to allow you to filter by:

      * Profile ids  - pass the `?ids=` query parameter
      * Profile type - pass the `?profile_type=` query parameter
      * Program type - pass the `?program_type=` query parameter
      * Program year - pass the `?program_year=` query parameter
      * Limit results - pass the `?limit=` query parameter
    """
    ids = NumberInFilter(
        field_name='id',
        lookup_expr='in'
    )
    profile_type = django_filters.CharFilter(
        field_name='profile_type__value',
        lookup_expr='iexact',
    )
    program_type = django_filters.CharFilter(
        field_name='program_type__value',
        lookup_expr='iexact',
    )
    program_year = django_filters.CharFilter(
        field_name='program_year__value',
        lookup_expr='iexact',
    )
    name = django_filters.CharFilter(method='filter_name')

    def filter_name(self, queryset, name, value):
        startswith_lookup = Q(custom_name__istartswith=value) | Q(related_user__name__istartswith=value)
        qs_startswith = queryset.filter(startswith_lookup)
        qs_contains = queryset.filter(
            Q(custom_name__icontains=value) | Q(related_user__name__icontains=value)
        ).exclude(startswith_lookup)
        return list(chain(qs_startswith, qs_contains))

    limit = django_filters.NumberFilter(method='filter_limit')

    def filter_limit(self, queryset, name, value):
        return queryset.limit(value)

    @property
    def qs(self):
        """
        Ensure that if the filter route is called without
        a legal filtering argument, we return an empty
        queryset, rather than every profile in existence.
        """

        request = self.request
        if request is None:
            return UserProfile.objects.none()

        queries = self.request.query_params
        if queries is None:
            return UserProfile.objects.none()

        if 'search' in queries:
            qs = super(ProfileCustomFilter, self).qs
        else:
            qs = UserProfile.objects.none()

        fields = ProfileCustomFilter.get_fields()
        for key in fields:
            if key in queries:
                qs = super(ProfileCustomFilter, self).qs

        return qs

    class Meta:
        """
        Required Meta class
        """
        model = UserProfile
        fields = [
            'ids',
            'profile_type',
            'program_type',
            'program_year',
            'is_active',
            'name',
            'limit'
        ]


class ProfilesPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'
    max_page_size = 50


class UserProfileListAPIView(ListAPIView):
    """
    Query Params:
        search=(search in name, affiliation, user_bio, user_bio_long, location)
        profile_type=
        program_type=
        program_year=
        is_active=(True or False)
        ordering=(id, custom_name, program_year) or negative (e.g. -id) to reverse.
        basic=

    One of the queries above must be specified to get a result set
    You can also control pagination using the following query params:
        page_size=(number)
        page=(number)
    """
    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
        SearchFilter,
    )
    ordering_fields = ('id', 'custom_name', 'program_year',)
    ordering = ('-id',)
    search_fields = (
        'custom_name',
        'related_user__name',
        'affiliation',
        'user_bio',
        'user_bio_long',
        'location',
    )
    pagination_class = ProfilesPagination

    filter_class = ProfileCustomFilter

    def get_queryset(self):
        request = self.request
        queries = self.request.query_params
        # If we are doing a specific search for is_active, return a filtered list for either
        # active or inactive profiles. If we are filtering based on anything else, filter out
        # inactive profiles by default.
        if 'is_active' in queries:
            queryset = UserProfile.objects.all().prefetch_related('related_user')
        else:
            queryset = UserProfile.objects.filter(is_active=True).prefetch_related('related_user')

        if not request or request.version != settings.API_VERSIONS['version_2']:
            # for all requests that aren't v2, we don't need to prefetch
            # anything else because no other relationship data is selected
            return queryset

        return queryset.prefetch_related(
            'issues',
            'profile_type',
            'program_type',
            'program_year',
            'bookmarks_from',
        )

    def paginate_queryset(self, queryset):
        request = self.request

        if not request:
            return super().paginate_queryset(queryset)

        version = request.version

        if version == settings.API_VERSIONS['version_1'] or version == settings.API_VERSIONS['version_2']:
            # Don't paginate version 1 and 2 of the API
            return None

        return super().paginate_queryset(queryset)

    def get_serializer_class(self):
        request = self.request

        if not request:
            # mock serializer testing
            return UserProfileListSerializer

        version = request.version

        if version == settings.API_VERSIONS['version_1']:
            # v1
            return UserProfilePublicWithEntriesSerializer

        if 'basic' in request.query_params:
            # v2 and above, 'basic' takes precedence over versioned serializers
            return UserProfileBasicSerializer

        if version == settings.API_VERSIONS['version_2']:
            # v2
            return UserProfilePublicSerializer

        # v3 and above
        return UserProfileListSerializer

    def get_serializer_context(self):
        return {
            'user': self.request.user
        }
