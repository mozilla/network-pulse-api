import json
from django.core.urlresolvers import reverse

from pulseapi.entries.models import Entry, ModerationState
from pulseapi.creators.models import EntryCreator
from pulseapi.tests import PulseMemberTestCase


class TestMemberEntryView(PulseMemberTestCase):
    def test_approval_requirement(self):
        """
        Verify that entries submitted by non-Mozilla emails
        aren't immediately visible
        """

        payload = self.generatePostPayload(
            data={'title': 'title test_approval_requirement'}
        )
        postresponse = self.client.post('/api/pulse/entries/', payload)
        self.assertEqual(postresponse.status_code, 200)

        responseobj = json.loads(str(postresponse.content, 'utf-8'))
        id = str(responseobj['id'])

        getresponse = self.client.get('/api/pulse/entries/' + id, follow=True)
        get_list_response = json.loads(
            str(self.client.get('/api/pulse/entries/').content, 'utf-8')
        )
        results = get_list_response['results']

        self.assertEqual(len(results), 2)
        self.assertEqual(getresponse.status_code, 404)

    def test_moderation_toggle_by_regular_joe(self):
        """
        Verify that only authorized users can moderate
        """

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
        self.assertEqual(response.status_code, 403)

        # and did it change the moderation state?
        entry = Entry.objects.get(id=entry_id)
        state = ModerationState.objects.get(name="Pending")
        self.assertEqual(entry.moderation_state, state)

    def test_anonymous_bookmark_route(self):
        """
        Verify that unauthorized users get an empty bookmark list.
        """

        # verify that unauthenticated users get a status 200 response
        self.client.logout()
        bookmark_response = self.client.get('/api/pulse/entries/bookmarks/')
        self.assertEqual(bookmark_response.status_code, 200)

        bookmark_json = json.loads(str(bookmark_response.content, 'utf-8'))

        # verify that data returned has the following properties and that 'count' is 0
        self.assertEqual('count' in bookmark_json, True)
        self.assertEqual('previous' in bookmark_json, True)
        self.assertEqual('next' in bookmark_json, True)
        self.assertEqual('results' in bookmark_json, True)
        self.assertEqual(len(bookmark_json), 4)
        self.assertEqual(bookmark_json['count'], 0)

    def test_creator_ordering(self):
        """
        Verify that posting entries preserves the order in which creators
        were passed to the system.
        """
        related_creators = [
            {'name': 'First Creator'},
            {'name': 'Second Creator'},
            {'name': 'Third Creator'},
        ]
        payload = self.generatePostPayload(data={
            'title': 'title test_creator_ordering',
            'content_url': 'http://example.org/test_creator_ordering',
            'related_creators': related_creators
        })

        response = self.client.post(reverse('entries-list'), payload)
        self.assertEqual(response.status_code, 200)

        entry_id = int(json.loads(str(response.content, 'utf-8'))['id'])
        entry_creators = EntryCreator.objects.filter(entry__id=entry_id).select_related('profile')
        self.assertEqual(len(entry_creators), len(related_creators))

        for creator, entry_creator in zip(related_creators, entry_creators):
            self.assertEqual(entry_creator.profile.custom_name, creator['name'])
