import base64
import django_filters

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404

from rest_framework import filters, permissions
from rest_framework.generics import RetrieveAPIView, RetrieveUpdateAPIView, ListCreateAPIView

from pulseapi.profiles.models import UserProfile
from pulseapi.profiles.serializers import (
    UserProfileSerializer,
    UserProfilePublicSerializer,
)


class IsProfileOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class UserProfilePublicAPIView(RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfilePublicSerializer


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


class UserProfileAPISearchView(ListCreateAPIView):
    serializer_class = UserProfileSerializer

    filter_backends = (
        filters.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    )

    filter_class = ProfileCustomFilter

    queryset = UserProfile.objects.all()
