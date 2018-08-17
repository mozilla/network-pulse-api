import base64
from django.core.files.base import ContentFile
from rest_framework import permissions
from rest_framework.generics import RetrieveUpdateAPIView, get_object_or_404

from pulseapi.profiles.models import UserProfile
from pulseapi.profiles.serializers import UserProfileSerializer


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

        try:
            thumbnail = payload['thumbnail']
            # do we actually need to repack as ContentFile?
            if thumbnail['name'] and thumbnail['base64']:
                name = thumbnail['name']
                encdata = thumbnail['base64']
                proxy = ContentFile(base64.b64decode(encdata), name=name)
                payload['thumbnail'] = proxy
        except KeyError:
            pass

        return super(UserProfileAPIView, self).put(request, *args, **kwargs)
