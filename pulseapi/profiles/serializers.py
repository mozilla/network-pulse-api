from rest_framework import serializers

from pulseapi.issues.models import Issue
from pulseapi.profiles.models import (
    UserProfile,
    UserBookmarks,
)
from pulseapi.entries.serializers import EntrySerializer


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
        required=False,
        allow_blank=True,
    )
    custom_name = serializers.CharField(
        max_length=70,
        required=False,
        allow_blank=True,
    )
    is_group = serializers.BooleanField(read_only=True)
    issues = serializers.SlugRelatedField(
        many=True,
        slug_field='name',
        queryset=Issue.objects,
        required=False
    )
    twitter = serializers.URLField(
        max_length=2048,
        required=False,
        allow_blank=True,
    )
    linkedin = serializers.URLField(
        max_length=2048,
        required=False,
        allow_blank=True,
    )
    github = serializers.URLField(
        max_length=2048,
        required=False,
        allow_blank=True,
    )
    website = serializers.URLField(
        max_length=2048,
        required=False,
        allow_blank=True,
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


class UserProfilePublicSerializer(UserProfileSerializer):
    """
    Serializes a user profile for public view
    """
    name = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name',
        source='user',
    )
    published_entries = serializers.SerializerMethodField()

    def get_published_entries(self, instance):
        return EntrySerializer(
            instance.user.entries.public(),
            context=self.context,
            many=True,
        ).data

    my_profile = serializers.SerializerMethodField()

    def get_my_profile(self, instance):
        return self.context.get('request').user == instance.user
