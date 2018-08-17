from rest_framework.generics import ListAPIView

from profiles.models import OrganizationProfile


class OrganizationProfileListAPIView(ListAPIView):
    """
    TODO: Docs
    """

    queryset = OrganizationProfile.objects.all().prefetch_related(
        'issues',
        'administrator'
    )
