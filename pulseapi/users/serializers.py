"""Serialize the models"""
from rest_framework import serializers


class EmailUserSerializer(serializers.ModelSerializer):
    """
    Serializes an EmailUser...
    """

    email = serializers.EmailField()
    name = serializers.CharField(max_length=1000)
    is_staff = serializers.BooleanField(default=False)
