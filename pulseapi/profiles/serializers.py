from rest_framework import serializers

from pulseapi.issues.models import Issue
from pulseapi.profiles.models import UserProfile, UserBookmarks


class UserBookmarksSerializer(serializers.ModelSerializer):
    """
    Serializes a {user,entry,when} bookmark.
    """

    class Meta:
        """
        Meta class. Again: because
        """
        model = UserBookmarks


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializes a user profile.
    """
    user_bio = serializers.CharField(
        max_length=140,
        required=False
    )
    custom_name = serializers.CharField(
        max_length=500,
        required=False
    )
    is_group = serializers.BooleanField()
    thumbnail = serializers.ImageField(
        max_length=2048,
        required=False
    )
    issues = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Issue.objects,
        required=True
    )
    twitter = serializers.URLField(
        max_length=2048,
        required=False
    )
    linkedin = serializers.URLField(
        max_length=2048,
        required=False
    )
    github = serializers.URLField(
        max_length=2048,
        required=False
    )
    website = serializers.URLField(
        max_length=2048,
        required=False
    )

    class Meta:
        """
        Meta class. Because
        """
        model = UserProfile
        exclude = [
            'is_active',
            'user',
            'bookmarks',
            'id',
        ]
