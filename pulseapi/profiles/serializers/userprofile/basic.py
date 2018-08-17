from rest_framework import serializers


class UserProfileBasicSerializer(serializers.BaseSerializer):
    """
    A read-only serializer that serializes a user profile by only including indentity
    information like `id` and `name`.
    """
    def to_representation(self, obj):
        return {
            'id': obj.id,
            'name': obj.name,
            'is_active': obj.is_active,
        }
