import base64
import django_filters

from django.core.files.base import ContentFile
from django.conf import settings

from rest_framework import filters, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import (
    get_object_or_404,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
    ListAPIView,
)

from pulseapi.profiles.models import UserProfile
from pulseapi.profiles.serializers import (
    UserProfileSerializer,
    UserProfilePublicSerializer,
    UserProfilePublicWithEntriesSerializer,
    UserProfileEntriesSerializer,
    UserProfileBasicSerializer,
)


class IsProfileOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class UserProfilePublicAPIView(RetrieveAPIView):
    queryset = UserProfile.objects.all()

    def get_serializer_class(self):
        if self.request.version == settings.API_VERSIONS['version_2']:
            return UserProfilePublicSerializer

        return UserProfilePublicWithEntriesSerializer


class UserProfilePublicSelfAPIView(UserProfilePublicAPIView):
    def get_object(self):
        user = self.request.user
        return get_object_or_404(self.queryset, related_user=user)


class UserProfileAPIView(RetrieveUpdateAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsProfileOwner
    )

    serializer_class = UserProfileSerializer

    def get_object(self):
        user = self.request.user
        return get_object_or_404(UserProfile, related_user=user)

    def put(self, request, *args, **kwargs):
        '''
        If there is a thumbnail, and it was sent as part of an
        application/json payload, then we need to unpack a thumbnail
        object payload and convert it to a Python ContentFile payload
        instead. We use a try/catch because the optional nature means
        we need to check using "if hasattr(request.data,'thumbnail'):"
        as we as "if request.data['thumbnail']" and these are pretty
        much mutually exclusive patterns. A try/pass make far more sense.
        '''

        payload = request.data

        try:
            thumbnail = payload['thumbnail']
            # do we actually need to repack as ContentFile?
            if thumbnail['name'] and thumbnail['base64']:
                name = thumbnail['name']
                encdata = thumbnail['base64']
                proxy = ContentFile(base64.b64decode(encdata), name=name)
                payload['thumbnail'] = proxy
        except:
            pass

        return super(UserProfileAPIView, self).put(request, *args, **kwargs)


# We don't inherit from a generic API view class since we're customizing
# the get functionality more than the generic would allow.
class UserProfileEntriesAPIView(APIView):
    authentication_classes = []

    def get(self, request, pk, **kwargs):
        """
        Return a list of entries associated with this profile
        that can be filtered by entries that this profile - was
        a creator on, was a publisher of, or favorited.
        """
        profile = get_object_or_404(
            UserProfile.objects.select_related(
                'related_creator',
                'related_user'
            ),
            pk=pk,
        )
        query = request.query_params

        return Response(
            UserProfileEntriesSerializer(instance=profile, context={
                'created': 'created' in query,
                'published': 'published' in query,
                'favorited': 'favorited' in query
            }).data
        )


# NOTE: DRF has deprecated the FilterSet class in favor of
# django_filters.rest_framework.FilterSet in v3.7.x, which
# we aren't far from upgrading to.
# SEE: https://github.com/mozilla/network-pulse-api/issues/288
class ProfileCustomFilter(filters.FilterSet):
    """
      We add custom filtering to allow you to filter by:

      * Profile type - pass the `?profile_type=` query parameter
      * Program type - pass the `?program_type=` query parameter
      * Program year - pass the `?program_year=` query parameter
    """
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

    @property
    def qs(self):
        """
        Ensure that if the filter route is called without
        a legal filtering argument, we return an empty
        queryset, rather than every profile in existence.
        """
        empty_set = UserProfile.objects.none()

        request = self.request
        if request is None:
            return empty_set

        queries = self.request.GET
        if queries is None:
            return empty_set

        fields = ProfileCustomFilter.get_fields()
        for key in fields:
            if key in queries:
                return super(ProfileCustomFilter, self).qs

        return empty_set

    class Meta:
        """
        Required Meta class
        """
        model = UserProfile
        fields = [
            'profile_type',
            'program_type',
            'program_year',
        ]


class UserProfileListAPIView(ListAPIView):
    """
      Query Params:
      profile_type=
      program_type=
      program_year=
      ordering=(custom_name, program_year) or negative (e.g. -custom_name) to reverse.
      basic
    """
    filter_backends = (
        filters.DjangoFilterBackend,
        filters.OrderingFilter,
    )

    ordering_fields = ('custom_name', 'program_year',)

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

        if request and request.version == settings.API_VERSIONS['version_2']:
            if request.query_params.get('basic'):
                return UserProfileBasicSerializer
            return UserProfilePublicSerializer

        return UserProfilePublicWithEntriesSerializer
