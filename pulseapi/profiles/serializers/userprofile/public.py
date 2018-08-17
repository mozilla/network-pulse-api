from rest_framework import serializers

from .serializer import UserProfileSerializer


class UserProfilePublicSerializer(UserProfileSerializer):
    """
    Serializes a user profile for public view
    """
    name = serializers.CharField(read_only=True)
    my_profile = serializers.SerializerMethodField()

    def get_my_profile(self, instance):
        user = self.context.get('user')
        return user == instance.user
