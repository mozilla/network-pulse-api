import json
from django.urls import reverse

from pulseapi.entries.models import Entry, ModerationState
from pulseapi.creators.models import EntryCreator
from pulseapi.tags.models import Tag
from pulseapi.tests import PulseMemberTestCase
from pulseapi.users.factory import BasicEmailUserFactory


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


class TestEntryAPIJSONView(PulseMemberTestCase):
    def setUp(self):
        super().setUp()

        (curricculum, created) = Tag.objects.get_or_create(name='curricculum')
        (libraries, created) = Tag.objects.get_or_create(name='libraries')

        cur_entry = Entry.objects.create(title='cur_entry', entry_type='news', published_by=self.user)
        cur_entry.set_moderation_state('Approved')
        cur_entry.tags.add(curricculum)
        cur_entry.save()

        lib_entry = Entry.objects.create(title='lib_entry', entry_type='news', published_by=self.user)
        lib_entry.set_moderation_state('Approved')
        lib_entry.tags.add(libraries)
        lib_entry.save()

        dual_entry = Entry.objects.create(title='dual_entry', entry_type='news', published_by=self.user)
        dual_entry.set_moderation_state('Approved')
        dual_entry.tags.add(curricculum)
        dual_entry.tags.add(libraries)
        dual_entry.save()

    def test_single_tag_search(self):
        response = self.client.get('/api/pulse/entries/?search=curricculum&format=json')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(str(response.content, 'utf-8'))
        count = response_data['count']
        self.assertEqual(count, 2)

        response = self.client.get('/api/pulse/entries/?search=libraries&format=json')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(str(response.content, 'utf-8'))
        count = response_data['count']
        self.assertEqual(count, 2)

    def test_dual_tag_search(self):
        response = self.client.get('/api/pulse/entries/?search=curricculum libraries&format=json')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(str(response.content, 'utf-8'))
        count = response_data['count']
        self.assertEqual(count, 1)

    def test_inactive_profile_entry_is_hidden(self):
        """
        Creating two entries of the same name, to test that the
        entry created by an inactive profile will be hidden from results.
        """
        entry_name = 'test_entry'

        test_entry = Entry.objects.create(title=entry_name, entry_type='news', published_by=self.user)
        test_entry.set_moderation_state('Approved')
        test_entry.save()

        inactive_profile_user = BasicEmailUserFactory.create(active=False)
        inactive_profile_entry = Entry.objects.create(
            title=entry_name, entry_type='news', published_by=inactive_profile_user)
        inactive_profile_entry.set_moderation_state('Approved')
        inactive_profile_entry.save()

        response = self.client.get(f'/api/pulse/entries/?search={test_entry}&format=json')
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(str(response.content, 'utf-8'))
        count = response_data['count']
        returned_entry = response_data['results'][0]
        self.assertEqual(count, 1)
        self.assertNotEqual(inactive_profile_entry.id, returned_entry['id'])
