from rest_framework.generics import ListAPIView, RetrieveAPIView

from pulsepapi.profiles.models import OrganizationProfile
from pulseapi.utility.viewutils import DefaultPagination
from pulseapi.profiles.serializers import OrganizationProfileSerializer


class OrganizationProfileListAPIView(ListAPIView):
    """
    View to list all the organization profiles
    """
    queryset = OrganizationProfile.objects.all().prefetch_related(
        'issues',
        'administrator',
    )
    serializer_class = OrganizationProfileSerializer
    pagination_class = DefaultPagination


class OrganizationProfileAPIView(RetrieveAPIView):
    """
    View to list all the organization profiles
    """
    queryset = OrganizationProfile.objects.all().prefetch_related(
        'issues',
        'administrator',
    )
    serializer_class = OrganizationProfileSerializer
    pagination_class = DefaultPagination
