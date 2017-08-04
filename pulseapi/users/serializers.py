"""Serialize the models"""
from rest_framework import serializers

from pulseapi.users.models import EmailUser


class EmailUserSerializer(serializers.ModelSerializer):
    """
    Serializes an EmailUser...
    """

    email = serializers.EmailField()
    name = serializers.CharField(max_length=1000)
    is_staff = serializers.BooleanField(default=False)
