"""
Provide RSS and Atom feeds for Pulse.
"""
from django.contrib.syndication.views import Feed
from django.urls import reverse

from pulseapi.entries.models import Entry


class LatestFromPulseFeed(Feed):
    title = "Latest from Mozilla Pulse"
    link = "/latest/"
    description_template = "Subscribe to get the latest entries from Mozilla Pulse."

    def items(self):
        return Entry.objects.order_by('-created')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return reverse('entry', args=[item.pk])
