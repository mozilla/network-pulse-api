"""Serialize the models"""
from rest_framework import serializers

from pulseapi.users.models import (
    EmailUser,
    UserBookmarks,
)


class UserBookmarksSerializer(serializers.ModelSerializer):
    """
    Serializes a {user,entry,when} bookmark.
    """

    class Meta:
        """
        Meta class. Again: because
        """
        model = UserBookmarks

class EmailUserSerializer(serializers.ModelSerializer):
    """
    Serializes an EmailUser...
    """

    email = serializers.EmailField()
    name = serializers.CharField(max_length=1000)
    is_staff = serializers.BooleanField(default=False)
