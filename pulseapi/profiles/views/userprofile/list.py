from itertools import chain

import django_filters
from django.conf import settings
from django.db.models import Q
from rest_framework import filters
from rest_framework.generics import ListAPIView

from pulseapi.profiles.models import UserProfile
from pulseapi.profiles.serializers import (
    UserProfilePublicWithEntriesSerializer,
    UserProfileBasicSerializer,
    UserProfilePublicSerializer
)


class NumberInFilter(django_filters.BaseInFilter, django_filters.NumberFilter):
    pass


# NOTE: DRF has deprecated the FilterSet class in favor of
# django_filters.rest_framework.FilterSet in v3.7.x, which
# we aren't far from upgrading to.
# SEE: https://github.com/mozilla/network-pulse-api/issues/288
class ProfileCustomFilter(filters.FilterSet):
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
        name='profile_type__value',
        lookup_expr='iexact',
    )
    program_type = django_filters.CharFilter(
        name='program_type__value',
        lookup_expr='iexact',
    )
    program_year = django_filters.CharFilter(
        name='program_year__value',
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
        qs = UserProfile.objects.none()

        request = self.request
        if request is None:
            return qs

        queries = self.request.query_params
        if queries is None:
            return qs

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


class UserProfileListAPIView(ListAPIView):
    """
      Query Params:
      profile_type=
      program_type=
      program_year=
      is_active=(True or False)
      ordering=(id, custom_name, program_year) or negative (e.g. -id) to reverse.
      basic=
    """
    filter_backends = (
        filters.OrderingFilter,
        filters.DjangoFilterBackend,
    )

    ordering_fields = ('id', 'custom_name', 'program_year',)

    filter_class = ProfileCustomFilter

    queryset = UserProfile.objects.all().prefetch_related(
        'related_user',
        'issues',
        'profile_type',
        'program_type',
        'program_year'
    )

    def get_serializer_class(self):
        request = self.request

        if request and request.version == settings.API_VERSIONS['version_1']:
            return UserProfilePublicWithEntriesSerializer

        if 'basic' in request.query_params:
            return UserProfileBasicSerializer
        return UserProfilePublicSerializer

    def get_serializer_context(self):
        return {
            'user': self.request.user
        }
