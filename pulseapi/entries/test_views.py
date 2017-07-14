import json

from django.core.urlresolvers import reverse

from pulseapi.entries.models import Entry, ModerationState
from pulseapi.tests import PulseStaffTestCase, PulseMemberTestCase


class TestEntryView(PulseStaffTestCase):
    def test_get_single_entry_data(self):
        """
        Check if we can get a single entry by its `id`
        """

        id = self.entries[0].id
        response = self.client.get(reverse('entry', kwargs={'pk': id}))
        self.assertEqual(response.status_code, 200)

    def test_post_minimum_entry(self):
        """
        Test posting an entry with minimum amount of content
        """

        payload = self.generatePostPayload(data={
            'title': 'title test_post_minimum_entry',
            'content_url': 'http://example.org/content/url'
        })
        postresponse = self.client.post('/api/pulse/entries/', payload)

        self.assertEqual(postresponse.status_code, 200)

    def test_post_duplicate_title(self):
        """Make sure multiple entries can have the same title"""

        payload = {
            'title': 'test_post_duplicate_title',
            'content_url': 'http://example.com/test1'
        }
        postresponse = self.client.post(
            '/api/pulse/entries/',
            data=self.generatePostPayload(data=payload)
        )

        payload = {
            'title': 'test_post_duplicate_title',
            'content_url': 'http://example.com/test2'
        }
        postresponse = self.client.post(
            '/api/pulse/entries/',
            data=self.generatePostPayload(data=payload)
        )

        entriesJson = json.loads(
            str(self.client.get('/api/pulse/entries/').content, 'utf-8')
        )
        self.assertEqual(postresponse.status_code, 200)
        self.assertEqual(len(entriesJson['results']), 4)

    def test_post_empty_title(self):
        """Make sure entries require a title"""

        payload = {
            'title': ''
        }
        postresponse = self.client.post(
            '/api/pulse/entries/',
            data=self.generatePostPayload(data=payload)
        )
        self.assertEqual(postresponse.status_code, 400)

    def test_post_content_url_empty(self):
        """Make sure entries require a content_url"""

        payload = {
            'content_url': ''
        }
        postresponse = self.client.post(
            '/api/pulse/entries/',
            data=self.generatePostPayload(data=payload)
        )
        self.assertEqual(postresponse.status_code, 400)

    def test_post_full_entry(self):
        """Entry with all content"""

        payload = {
            'title': 'test full entry',
            'description': 'description full entry',
            'tags': ['tag1', 'tag2'],
            'interest': 'interest field',
            'get_involved': 'get involved text field',
            'get_involved_url': 'http://example.com/getinvolved',
            'content_url': 'http://example.com/',
            'internal_notes': 'Some internal notes',
            'featured': True,
            'issues': 'Decentralization',
            'creators': ['Pomax', 'Alan']
        }
        postresponse = self.client.post(
            '/api/pulse/entries/',
            data=self.generatePostPayload(data=payload)
        )
        self.assertEqual(postresponse.status_code, 200)

    def test_featured_filter(self):
        """Entry with all content"""

        payload = {
            'title': 'test full entry',
            'description': 'description full entry',
            'tags': ['tag1', 'tag2'],
            'interest': 'interest field',
            'get_involved': 'get involved text field',
            'get_involved_url': 'http://example.com/getinvolved',
            'content_url': 'http://example.com/',
            'internal_notes': 'Some internal notes',
            'featured': True,
            'issues': 'Decentralization',
            'creators': ['Pomax', 'Alan']
        }
        postresponse = self.client.post(
            '/api/pulse/entries/',
            data=self.generatePostPayload(data=payload)
        )
        responseobj = json.loads(str(postresponse.content, 'utf-8'))
        entryId = responseobj['id']
        # this entry should not be featured automatically
        searchList = self.client.get('/api/pulse/entries/?featured=True')
        entriesJson = json.loads(str(searchList.content, 'utf-8'))
        self.assertEqual(len(entriesJson['results']), 0)
        # toggle this entry's feature flag
        entry = Entry.objects.get(id=entryId)
        entry.featured = True
        entry.save()
        # This entry should now show up as featured
        searchList = self.client.get('/api/pulse/entries/?featured=True')
        entriesJson = json.loads(str(searchList.content, 'utf-8'))
        self.assertEqual(len(entriesJson['results']), 1)

    def test_post_entry_with_mixed_tags(self):
        """
        Post entries with some existing tags, some new tags
        See if tags endpoint has proper results afterwards
        """

        content_url = 'http://example.com/test_post_entry_with_mixed_tags_1'
        payload = {
            'title': 'title test_post_entry_with_mixed_tags2',
            'content_url': content_url,
            'tags': ['test1', 'test2'],
        }
        self.client.post(
            '/api/pulse/entries/',
            data=self.generatePostPayload(data=payload)
        )
        content_url = 'http://example.com/test_post_entry_with_mixed_tags_2'
        payload = {
            'title': 'title test_post_entry_with_mixed_tags2',
            'content_url': content_url,
            'tags': ['test2', 'test3'],
        }
        self.client.post(
            '/api/pulse/entries/',
            data=self.generatePostPayload(data=payload)
        )
        tagList = json.loads(
            str(self.client.get('/api/pulse/tags/').content, 'utf-8')
        )
        self.assertEqual(tagList, ['test1', 'test2', 'test3'])

    def test_post_entry_with_mixed_creators(self):
        """
        Post entry with some existing creators, some new creators
        See if creators endpoint has proper results afterwards
        """

        payload = {
            'title': 'title test_post_entry_with_mixed_tags2',
            'description': 'description test_post_entry_with_mixed_tags',
            'creators': ['Pomax', 'Alan'],
        }
        json.loads(
            str(self.client.get('/api/pulse/nonce/').content, 'utf-8')
        )
        self.client.post(
            '/api/pulse/entries/',
            data=self.generatePostPayload(data=payload)
        )
        creatorList = json.loads(
            str(self.client.get('/api/pulse/creators/').content, 'utf-8')
        )
        self.assertEqual(creatorList, ['Pomax', 'Alan'])

    def test_get_entries_list(self):
        """Get /entries endpoint"""

        entryList = self.client.get('/api/pulse/entries/')
        self.assertEqual(entryList.status_code, 200)

    def test_entries_search(self):
        """Make sure filtering searches works"""

        payload = {
            'title': 'test_entries_search',
            'content_url': 'http://example.com/setup',
            'description': 'test setup'
        }
        self.client.post(
            '/api/pulse/entries/',
            data=self.generatePostPayload(data=payload)
        )
        searchList = self.client.get('/api/pulse/entries/?search=setup')
        entriesJson = json.loads(str(searchList.content, 'utf-8'))
        self.assertEqual(len(entriesJson['results']), 1)

    def test_entries_pagination(self):
        """Make sure pagination works"""

        page1 = self.client.get('/api/pulse/entries/?page=1&page_size=1')
        page2 = self.client.get('/api/pulse/entries/?page=2&page_size=1')
        page1Json = json.loads(str(page1.content, 'utf-8'))
        page2Json = json.loads(str(page2.content, 'utf-8'))
        self.assertEqual(len(page1Json['results']), 1)
        self.assertEqual(len(page2Json['results']), 1)
        self.assertNotEqual(
            page1Json['results'][0]['title'],
            page2Json['results'][0]['title']
        )

    def test_entries_search_by_tag(self):
        """Make sure filtering searches by tag works"""

        payload = {
            'title': 'title test_entries_issue',
            'content_url': 'http://example.com/test_entries_search_by_tag',
            'tags': ['tag1']
        }
        json.loads(str(self.client.get('/api/pulse/nonce/').content, 'utf-8'))
        self.client.post(
            '/api/pulse/entries/',
            data=self.generatePostPayload(data=payload)
        )
        searchList = self.client.get('/api/pulse/entries/?tag=tag1')
        entriesJson = json.loads(str(searchList.content, 'utf-8'))
        self.assertEqual(len(entriesJson['results']), 1)

    def test_entries_issue(self):
        """test filtering entires by issue"""

        payload = {
            'title': 'title test_entries_issue',
            'description': 'description test_entries_issue',
            'issues': 'Decentralization',
        }
        json.loads(
            str(self.client.get('/api/pulse/nonce/').content, 'utf-8')
        )
        self.client.post(
            '/api/pulse/entries/',
            data=self.generatePostPayload(data=payload)
        )
        url = '/api/pulse/entries/?issue=Decentralization'
        searchList = self.client.get(url)
        entriesJson = json.loads(str(searchList.content, 'utf-8'))
        self.assertEqual(len(entriesJson['results']), 1)

    def test_post_entry_new_issue(self):
        """
        posting an entry with a new Issue should result
        in an error. Permission denied?
        """

        payload = {
            'title': 'title test_entries_issue',
            'description': 'description test_entries_issue',
            'issues': 'Privacy',
        }
        postresponse = self.client.post(
            '/api/pulse/entries/',
            data=self.generatePostPayload(data=payload)
        )
        self.assertEqual(postresponse.status_code, 400)

    def test_post_authentication_requirement(self):
        """Make sure you can't post without using the nonce"""

        postresponse = self.client.post('/api/pulse/entries/', data={
            'title': 'title this test should fail',
            'description': 'description this test should fail',
            'tags': ['tag2', 'tag3'],
            'interest': 'interest field',
            'get_involved': 'get involved text field',
            'get_involved_url': 'http://example.com/getinvolved',
            'content_url': 'http://example.com/',
            'internal_notes': 'Some internal notes'
        })
        self.assertEqual(postresponse.status_code, 400)

    def test_put_bookmark_entry_without_login(self):
        """
        Verify that anonymous users cannot bookmark entries.
        """

        # get a legal entry and its associated id
        entries = Entry.objects.all()
        entry = entries[0]
        id = entry.id

        # ensure the user is logged out, then try to bookmark
        self.client.logout()
        url = '/api/pulse/entries/' + str(id) + '/bookmark'
        postresponse = self.client.put(url)
        self.assertEqual(postresponse.status_code, 403)

        # verify bookmark count is zero
        bookmarks = entry.bookmarked_by.count()
        self.assertEqual(bookmarks, 0)

    def test_put_bookmark_entry_with_login(self):
        """
        Verify that authenticated users can (un)bookmark an entry.
        """

        # get a legal entry and its associated id
        entries = Entry.objects.all()
        entry = entries[0]
        id = entry.id

        put_url = '/api/pulse/entries/' + str(id) + '/bookmark'

        postresponse = self.client.put(put_url)
        self.assertEqual(postresponse.status_code, 204)

        # verify bookmark count is now one
        bookmarks = entry.bookmarked_by.count()
        self.assertEqual(bookmarks, 1)

        # put again, which should clear the bookmark flag for this user
        postresponse = self.client.put(put_url)
        self.assertEqual(postresponse.status_code, 204)

        # verify bookmark count is now zero
        bookmarks = entry.bookmarked_by.count()
        self.assertEqual(bookmarks, 0)

    def test_bookmarked_entries_view(self):
        """
        Verify that authenticated users can see a list of bookmarks.
        """
        # get a legal entry and its associated id
        entries = Entry.objects.all()
        entry = entries[0]
        id = entry.id

        self.client.put('/api/pulse/entries/' + str(id) + '/bookmark')

        # verify bookmark count is now one
        bookmarkResponse = self.client.get('/api/pulse/entries/bookmarks/')
        self.assertEqual(bookmarkResponse.status_code, 200)

        # verify data returned has the following properties
        bookmarkJson = json.loads(str(bookmarkResponse.content, 'utf-8'))

        self.assertEqual('count' in bookmarkJson, True)
        self.assertEqual('previous' in bookmarkJson, True)
        self.assertEqual('next' in bookmarkJson, True)
        self.assertEqual('results' in bookmarkJson, True)
        self.assertEqual(len(bookmarkJson), 4)

    def test_moderation_states(self):
        mod_set = ModerationState.objects.all()
        mod_count = len(mod_set)

        url = '/api/pulse/entries/moderation-states/?format=json'
        moderation_states = self.client.get(url)
        responseObj = json.loads(str(moderation_states.content, 'utf-8'))
        self.assertEqual(len(responseObj), mod_count)
        self.assertEqual(responseObj[0]['name'], "Pending")


    def test_moderation_toggle_by_staff(self):
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
