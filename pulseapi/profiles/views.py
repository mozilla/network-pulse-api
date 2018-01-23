import base64

from django.core.files.base import ContentFile
from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework import permissions
from rest_framework.decorators import detail_route
from rest_framework.generics import RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.parsers import JSONParser

from rest_framework.exceptions import UnsupportedMediaType


from pulseapi.profiles.models import UserProfile
from pulseapi.profiles.serializers import (
    UserProfileSerializer,
    UserProfilePublicSerializer,
)


# utility function for removing keyed values, with key, from a dict
def removeKey(container, property):
    try:
        del(container, property)
    except:
        pass


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

    parser_classes = (
        JSONParser,
    )

    def get_object(self, queryset=None):
        if self.request.method == "PUT":
            profile = super(UserProfileAPIView, self).get_object(queryset=queryset)
            if profile is None:
                raise Http404()
            return profile

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

        # THIS CURRENTLY THROWS A UnsupportedMediaType
        # ERROR FOR THE APPLICATION/JSON MEDIA TYPE O_o
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

        '''
        Is there an 'enable_extended_information' property? If so,
        this is something that may only be toggled by admins and
        cannot be toggled through general profile updates
        '''

        removeKey(payload, 'enable_extended_information')

        '''
        Do a prefetch on the profile to update. Is the
        'enable_extended_information' property set to False?
        In that case, remove any extended properties from the
        request payload.
        '''

        try:
            user = self.request.user
            profile = UserProfile.objects.get(related_user=user)

            print(profile)

            if profile.enable_extended_information is False:
                removeKey(payload, 'user_bio_long')
                removeKey(payload, 'program_type')
                removeKey(payload, 'program_year')
                removeKey(payload, 'affiliation')

        except:
            # This user has no associated profile, which should
            # be impossible, but let's catch for it, anyway.
            pass

        return super(UserProfileAPIView, self).put(request, *args, **kwargs)
