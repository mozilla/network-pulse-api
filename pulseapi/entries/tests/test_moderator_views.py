import json

from django.core.urlresolvers import reverse
from django.db.models import Q
from django.test.client import MULTIPART_CONTENT
from rest_framework import status

from pulseapi.creators.models import Creator, OrderedCreatorRecord
from pulseapi.entries.models import Entry, ModerationState
from pulseapi.entries.serializers import EntrySerializer
from pulseapi.tests import PulseModeratorTestCase


class TestModeratorEntryView(PulseModeratorTestCase):
    def test_moderation_states(self):
        mod_set = ModerationState.objects.all()
        mod_count = len(mod_set)

        url = '/api/pulse/entries/moderation-states/?format=json'
        moderation_states = self.client.get(url)
        responseObj = json.loads(str(moderation_states.content, 'utf-8'))
        self.assertEqual(len(responseObj), mod_count)
        self.assertEqual(responseObj[0]['name'], "Pending")

    def test_featured_toggle_without_login(self):
        entry = Entry.objects.all()[0]
        # ensure that featured status is False
        entry.featured = False
        entry.save()

        # ensure that user is logged out
        self.client.logout()

        url = '/api/pulse/entries/{}/feature'.format(entry.id)
        response = self.client.put(url)

        self.assertEqual(response.status_code, 403)

        entry.refresh_from_db()
        self.assertEqual(entry.featured, False)

    def test_featured_toggle_by_moderator(self):
        entry = Entry.objects.all()[0]
        # ensure that featured status is False
        entry.featured = False
        entry.save()

        url = '/api/pulse/entries/{}/feature'.format(entry.id)
        response = self.client.put(url)

        # did the call succeed?
        self.assertEqual(response.status_code, 204)

        entry.refresh_from_db()
        self.assertEqual(entry.featured, True)

    def test_moderation_toggle_by_moderator(self):
        entry = Entry.objects.all()[0]
        entry_id = str(entry.id)

        # ensure this entry is pending
        state = ModerationState.objects.get(name="Pending")
        entry.moderation_state = state
        entry.save()

        # try to moderate this entry to "approved"
        state = ModerationState.objects.get(name="Approved")
        state_id = str(state.id)
        url = '/api/pulse/entries/' + entry_id + '/moderate/' + state_id
        response = self.client.put(url)

        # did the call succeed?
        self.assertEqual(response.status_code, 204)

        # and did it change the moderation state?
        entry = Entry.objects.get(id=entry_id)
        self.assertEqual(entry.moderation_state, state)

