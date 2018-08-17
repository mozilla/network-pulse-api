from django.conf import settings
from rest_framework.generics import RetrieveAPIView

from profiles.models import UserProfile
from pulseapi.profiles.serializers import UserProfilePublicWithEntriesSerializer, UserProfilePublicSerializer


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