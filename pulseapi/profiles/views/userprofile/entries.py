from django.conf import settings
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from pulseapi.entries.serializers import EntryWithCreatorsBaseSerializer, EntryWithV1CreatorsBaseSerializer
from pulseapi.profiles.models import UserProfile
from pulseapi.profiles.serializers import UserProfileEntriesSerializer


# We don't inherit from a generic API view class since we're customizing
# the get functionality more than the generic would allow.
class UserProfileEntriesAPIView(APIView):
    def get(self, request, pk, **kwargs):
        """
        Return a list of entries associated with this profile
        that can be filtered by entries that this profile - was
        a creator on, was a publisher of, or favorited.
        """
        profile = get_object_or_404(
            UserProfile.objects.select_related('related_user'),
            pk=pk,
        )
        query = request.query_params
        EntrySerializerClass = EntryWithCreatorsBaseSerializer

        if request and request.version == settings.API_VERSIONS['version_1']:
            EntrySerializerClass = EntryWithV1CreatorsBaseSerializer

        return Response(
            UserProfileEntriesSerializer(instance=profile, context={
                'user': request.user,
                'created': 'created' in query,
                'published': 'published' in query,
                'favorited': 'favorited' in query,
                'created_ordering': query.get('created_ordering'),
                'published_ordering': query.get('published_ordering'),
                'favorited_ordering': query.get('favorited_ordering'),
                'EntrySerializerClass': EntrySerializerClass,
            }).data
        )