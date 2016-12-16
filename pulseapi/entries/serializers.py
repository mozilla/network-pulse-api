"""Serialize the models"""
from rest_framework import serializers
from django.utils.encoding import smart_text
from django.core.exceptions import ObjectDoesNotExist

from pulseapi.entries.models import(
    Entry,
)
from pulseapi.tags.models import(
    Tag,
)
from pulseapi.issues.models import(
    Issue,
)

class CreatableSlugRelatedField(serializers.SlugRelatedField):
    """
    Override SlugRelatedField to create or update
    instead of getting upset that a tag doesn't exist
    """
    def to_internal_value(self, data):
        try:
            return self.get_queryset().get_or_create(**{self.slug_field: data})[0]
        except ObjectDoesNotExist:
            self.fail('does_not_exist', slug_name=self.slug_field, value=smart_text(data))
        except (TypeError, ValueError):
            self.fail('invalid')

class EntrySerializer(serializers.ModelSerializer):
    """
    Serializes an entry with embeded information including
    list of tags, categories and links associated with that entry
    as simple strings. It also includes a list of hyperlinks to events
    that are associated with this entry as well as hyperlinks to users
    that are involved with the entry
    """

    tags = CreatableSlugRelatedField(many=True, slug_field='name', queryset=Tag.objects)
    issues = serializers.SlugRelatedField(many=True,
                                          slug_field='name',
                                          queryset=Issue.objects)

    class Meta:
        """
        Meta class. Because
        """
        model = Entry
        exclude = ('internal_notes',)
