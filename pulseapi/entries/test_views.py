import json

from django.core.urlresolvers import reverse

from pulseapi.creators.models import Creator, OrderedCreatorRecord
from pulseapi.entries.models import Entry, ModerationState
from pulseapi.entries.serializers import EntrySerializer
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

    def test_post_entry_with_comma_infused_tags(self):
        """
        Post entries with some existing tags, some new tags
        See if tags endpoint has proper results afterwards
        """

        content_url = 'http://example.com/test_post_entry_with_comma_infused_tags'
        payload = {
            'title': 'title test_post_entry_with_comma_infused_tags',
            'content_url': content_url,
            'tags': ['test1', 'test2', 'test1,test2,test3'],
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

        creators = ['Pomax', 'Alan']
        payload = {
            'title': 'title test_post_entry_with_mixed_tags2',
            'description': 'description test_post_entry_with_mixed_tags',
            'creators': creators,
        }
        json.loads(
            str(self.client.get('/api/pulse/nonce/').content, 'utf-8')
        )
        self.client.post(
            '/api/pulse/entries/',
            data=self.generatePostPayload(data=payload)
        )
        creator_list = json.loads(
            str(self.client.get('/api/pulse/creators/').content, 'utf-8')
        )
        db_creator_list = list(Creator.objects.values_list('name', flat=True))
        self.assertEqual(db_creator_list, creator_list)

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

    def test_entry_published_by(self):
        """Make sure entry includes publisher's full name as the published_by meta"""

        entry = Entry.objects.all()[0]
        id = self.entries[0].id
        response = self.client.get(reverse('entry', kwargs={'pk': id}))
        self.assertEqual(entry.published_by.name, response.data['published_by'])

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

    def test_entries_help_type(self):
        """test filtering entires by help_type"""

        payload = {
            'title': 'title test_entries_help_type',
            'description': 'description test_entries_help_type',
            'help_types': ['Write documentation', 'Code'],
        }
        json.loads(
            str(self.client.get('/api/pulse/nonce/').content, 'utf-8')
        )
        self.client.post(
            '/api/pulse/entries/',
            data=self.generatePostPayload(data=payload)
        )
        url = '/api/pulse/entries/?help_type=Code'
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

        # verify that authenticated users get a status 200 response
        bookmarkResponse = self.client.get('/api/pulse/entries/bookmarks/')
        self.assertEqual(bookmarkResponse.status_code, 200)

        # verify that data returned has the following properties
        bookmarkJson = json.loads(str(bookmarkResponse.content, 'utf-8'))

        self.assertEqual('count' in bookmarkJson, True)
        self.assertEqual('previous' in bookmarkJson, True)
        self.assertEqual('next' in bookmarkJson, True)
        self.assertEqual('results' in bookmarkJson, True)
        self.assertEqual(len(bookmarkJson), 4)

        # verify that bookmarkJson.results has the right content
        self.assertEqual(len(bookmarkJson['results']), 1)
        self.assertEqual(id, bookmarkJson['results'][0]['id'])

    def test_post_bookmark_entries_without_login(self):
        """
        Verify that anonymous users cannot bookmark a list of entries.
        """

        # get a legal entry and its associated id
        entries = Entry.objects.all()
        entry = entries[0]
        id = entry.id

        # ensure the user is logged out, then try to bookmark
        self.client.logout()
        url = '/api/pulse/entries/bookmarks/?ids=' + str(id)
        postresponse = self.client.post(url)
        self.assertEqual(postresponse.status_code, 403)

        # verify bookmark count is zero
        bookmarks = entry.bookmarked_by.count()
        self.assertEqual(bookmarks, 0)

    def test_post_bookmark_entries_with_login(self):
        """
        Verify that authenticated users can bookmark a list of entries.
        """

        # get two legal entries and their associated id
        entries = Entry.objects.all()
        entry1 = entries[0]
        id1 = entry1.id
        entry2 = entries[1]
        id2 = entry2.id

        # verify bookmark count for entry1 is zero
        bookmarks1 = entry1.bookmarked_by.count()
        self.assertEqual(bookmarks1, 0)

        # verify bookmark count for entry2 is now zero
        bookmarks2 = entry2.bookmarked_by.count()
        self.assertEqual(bookmarks2, 0)

        # bookmark entry1
        url = '/api/pulse/entries/bookmarks/?ids=' + str(id1)
        payload = self.generatePostPayload()

        postresponse = self.client.post(url, payload)
        self.assertEqual(postresponse.status_code, 204)

        # verify bookmark count for entry1 is now one
        bookmarks = entry1.bookmarked_by.count()
        self.assertEqual(bookmarks, 1)

        # now we bulk bookmark entry1 and entry2
        url = '/api/pulse/entries/bookmarks/?ids=' + str(id1) + ',' + str(id2)
        payload = self.generatePostPayload()

        postresponse = self.client.post(url, payload)
        self.assertEqual(postresponse.status_code, 204)

        # verify bookmark count for entry1 is still one
        bookmarks1 = entry1.bookmarked_by.count()
        self.assertEqual(bookmarks1, 1)

        # verify bookmark count for entry2 is now one
        bookmarks2 = entry2.bookmarked_by.count()
        self.assertEqual(bookmarks2, 1)

    def test_post_bookmark_entries_with_invalid_param(self):
        """
        Verify that bookmarking a list of entries with invalid ids
        will return a status 204
        """

        # get a non-existent id
        entries = Entry.objects.all()
        nonExistentId = len(entries) + 1

        url = '/api/pulse/entries/bookmarks/?ids=' + str(nonExistentId)
        payload = self.generatePostPayload()

        postresponse = self.client.post(url, payload)
        self.assertEqual(postresponse.status_code, 204)

        # post with a non-existent id
        invalidId = 'abc'

        url = '/api/pulse/entries/bookmarks/?ids=' + invalidId
        payload = self.generatePostPayload()

        postresponse = self.client.post(url, payload)
        self.assertEqual(postresponse.status_code, 204)

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

    def test_featured_toggle_by_staff(self):
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

    def test_entry_serializer(self):
        """
        Make sure that the entry serializer contains all the custom data needed.
        Useful test to make sure our custom fields are tested and not
        removed during API changes
        """

        entries = self.entries
        serialized_entries = EntrySerializer(entries, many=True).data

        for i in range(len(serialized_entries)):
            entry = entries[i]
            serialized_entry = dict(serialized_entries[i])
            # Make sure that the property exists in the serialized entry
            self.assertIn('creators_with_profiles', serialized_entry)
            creators_with_profiles = serialized_entry['creators_with_profiles']
            # Make sure that the number of serialized creators matches the
            # number of creators for that entry in the db
            self.assertEqual(
                len(creators_with_profiles),
                OrderedCreatorRecord.objects.filter(entry=entry).count()
            )


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
