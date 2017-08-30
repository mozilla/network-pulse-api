from django.shortcuts import get_object_or_404

from rest_framework import permissions
from rest_framework.generics import RetrieveAPIView, RetrieveUpdateAPIView

from pulseapi.profiles.models import UserProfile
from pulseapi.profiles.serializers import UserProfileSerializer


class IsProfileOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class UserProfileRetrieveAPIView(RetrieveAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class UserProfileAPIView(RetrieveUpdateAPIView):
    permission_classes = (
        permissions.IsAuthenticated,
        IsProfileOwner
    )
    serializer_class = UserProfileSerializer

    def get_object(self):
        user = self.request.user
        return get_object_or_404(UserProfile, user=user)
