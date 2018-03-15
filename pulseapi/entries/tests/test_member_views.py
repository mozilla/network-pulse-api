import json

from pulseapi.entries.models import Entry, ModerationState
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
        getListresponse = json.loads(
            str(self.client.get('/api/pulse/entries/').content, 'utf-8')
        )
        results = getListresponse['results']

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
        bookmarkResponse = self.client.get('/api/pulse/entries/bookmarks/')
        self.assertEqual(bookmarkResponse.status_code, 200)

        bookmarkJson = json.loads(str(bookmarkResponse.content, 'utf-8'))

        # verify that data returned has the following properties and that 'count' is 0
        self.assertEqual('count' in bookmarkJson, True)
        self.assertEqual('previous' in bookmarkJson, True)
        self.assertEqual('next' in bookmarkJson, True)
        self.assertEqual('results' in bookmarkJson, True)
        self.assertEqual(len(bookmarkJson), 4)
        self.assertEqual(bookmarkJson['count'], 0)

    def test_creator_ordering(self):
        """
        Verify that posting entries preserves the order in which creators
        were passed to the system.
        """

        payload = self.generatePostPayload(data={
            'title': 'title test_creator_ordering',
            'content_url': 'http://example.org/test_creator_ordering',
            'creators': [
              'First Creator',
              'Second Creator',
            ]
        })

        postresponse = self.client.post('/api/pulse/entries/', payload)
        content = str(postresponse.content, 'utf-8')
        response = json.loads(content)
        id = int(response['id'])
        entry = Entry.objects.get(id=id)
        creators = [c.creator for c in entry.related_creators.all()]

        self.assertEqual(creators[0].name, 'First Creator')
        self.assertEqual(creators[1].name, 'Second Creator')

        payload = self.generatePostPayload(data={
            'title': 'title test_creator_ordering',
            'content_url': 'http://example.org/test_creator_ordering',
            'creators': [
              # note that this is a different creator ordering
              'Second Creator',
              'First Creator',
            ]
        })

        postresponse = self.client.post('/api/pulse/entries/', payload)
        content = str(postresponse.content, 'utf-8')
        response = json.loads(content)
        id = int(response['id'])
        entry = Entry.objects.get(id=id)
        creators = [c.creator for c in entry.related_creators.all()]

        # the same ordering should be reflected in the creator list
        self.assertEqual(creators[0].name, 'Second Creator')
        self.assertEqual(creators[1].name, 'First Creator')
