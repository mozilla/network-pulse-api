import json

from django.core.urlresolvers import reverse

from pulseapi.entries.models import Entry
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
        payload = self.generatePostPayload(data={'title':'title test_post_minimum_entry', 'tags':''})
        postresponse = self.client.post('/entries/', payload)

        self.assertEqual(postresponse.status_code, 200)

    def test_post_duplicate_title(self):
        """Make sure multiple entries can have the same title"""

        payload = {
            'title': 'title setUp1',
        }
        postresponse = self.client.post('/entries/', data=self.generatePostPayload(data=payload))
        entriesJson = json.loads(str(self.client.get('/entries/').content, 'utf-8'))
        self.assertEqual(postresponse.status_code, 200)
        self.assertEqual(len(entriesJson['results']), 4)

    def test_post_empty_title(self):
        """Make sure entries require a title"""
        payload = {
            'title':''
        }
        postresponse = self.client.post('/entries/', data=self.generatePostPayload(data=payload))
        self.assertEqual(postresponse.status_code, 400)

    def test_post_content_url_empty(self):
        """Make sure entries require a content_url"""
        payload = {
            'content_url':''
        }
        postresponse = self.client.post('/entries/', data=self.generatePostPayload(data=payload))
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
            'thumbnail_url': 'http://example.com/',
            'content_url': 'http://example.com/',
            'internal_notes': 'Some internal notes',
            'featured': True,
            'issues': 'Decentralization',
            'creators': ['Pomax', 'Alan']
        }
        postresponse = self.client.post('/entries/', data=self.generatePostPayload(data=payload))
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
            'thumbnail_url': 'http://example.com/',
            'content_url': 'http://example.com/',
            'internal_notes': 'Some internal notes',
            'featured': True,
            'issues': 'Decentralization',
            'creators': ['Pomax', 'Alan']
        }
        postresponse = self.client.post('/entries/', data=self.generatePostPayload(data=payload))
        responseobj = json.loads(str(postresponse.content,'utf-8'))
        entryId = responseobj['id']
        # this entry should not be featured automatically
        searchList = self.client.get('/entries/?featured=True')
        entriesJson = json.loads(str(searchList.content, 'utf-8'))
        self.assertEqual(len(entriesJson['results']), 0)
        # toggle this entry's feature flag
        entry = Entry.objects.get(id=entryId)
        entry.featured = True
        entry.save()
        # This entry should now show up as featured
        searchList = self.client.get('/entries/?featured=True')
        entriesJson = json.loads(str(searchList.content, 'utf-8'))
        self.assertEqual(len(entriesJson['results']), 1)

    def test_post_entry_with_mixed_tags(self):
        """
        Post entries with some existing tags, some new tags
        See if tags endpoint has proper results afterwards
        """
        payload = {
            'title': 'title test_post_entry_with_mixed_tags2',
            'description': 'description test_post_entry_with_mixed_tags',
            'tags': ['tag2', 'tag3'],
        }
        values = json.loads(str(self.client.get('/nonce/').content, 'utf-8'))
        postresponse = self.client.post('/entries/', data=self.generatePostPayload(data=payload))
        tagList = json.loads(str(self.client.get('/tags/').content, 'utf-8'))
        self.assertEqual(tagList, ['tag1','tag2','tag3'])


    def test_post_entry_with_mixed_creators(self):
        """
        Post entry with some existing creators, some new creators
        See if creators endpoint has proper results afterwards
        """
        payload = {
            'title': 'title test_post_entry_with_mixed_tags2',
            'description': 'description test_post_entry_with_mixed_tags',
            'creators': ['Pomax','Alan'],
        }
        values = json.loads(str(self.client.get('/nonce/').content, 'utf-8'))
        postresponse = self.client.post('/entries/', data=self.generatePostPayload(data=payload))
        creatorList = json.loads(str(self.client.get('/creators/').content, 'utf-8'))
        self.assertEqual(creatorList, ['Pomax','Alan'])

    def test_get_entries_list(self):
        """Get /entries endpoint"""
        entryList = self.client.get('/entries/')
        self.assertEqual(entryList.status_code, 200)

    def test_entries_search(self):
        """Make sure filtering searches works"""
        searchList = self.client.get('/entries/?search=setup')
        entriesJson = json.loads(str(searchList.content, 'utf-8'))
        self.assertEqual(len(entriesJson['results']), 1)

    def test_entries_pagination(self):
        """Make sure pagination works"""
        page1 = self.client.get('/entries/?page=1&page_size=1')
        page2 = self.client.get('/entries/?page=2&page_size=1')
        page1Json = json.loads(str(page1.content, 'utf-8'))
        page2Json = json.loads(str(page2.content, 'utf-8'))
        self.assertEqual(len(page1Json['results']), 1)
        self.assertEqual(len(page2Json['results']), 1)
        self.assertNotEqual(page1Json['results'][0]['title'], page2Json['results'][0]['title'])

    def test_entries_search(self):
        """Make sure filtering searches by tag works"""
        searchList = self.client.get('/entries/?tag=tag1')
        entriesJson = json.loads(str(searchList.content, 'utf-8'))
        self.assertEqual(len(entriesJson['results']), 1)


    def test_entries_issue(self):
        """test filtering entires by issue"""
        payload = {
            'title': 'title test_entries_issue',
            'description': 'description test_entries_issue',
            'issues': 'Decentralization',
        }
        values = json.loads(str(self.client.get('/nonce/').content, 'utf-8'))
        postresponse = self.client.post('/entries/', data=self.generatePostPayload(data=payload))
        searchList = self.client.get('/entries/?issue=Decentralization')
        entriesJson = json.loads(str(searchList.content, 'utf-8'))
        self.assertEqual(len(entriesJson['results']), 1)

    def test_post_entry_new_issue(self):
        """posting an entry with a new Issue should result in an error. Permission denied?"""
        payload = {
            'title': 'title test_entries_issue',
            'description': 'description test_entries_issue',
            'issues': 'Privacy',
        }
        postresponse = self.client.post('/entries/', data=self.generatePostPayload(data=payload))
        self.assertEqual(postresponse.status_code, 400)

    def test_post_authentication_requirement(self):
        """Make sure you can't post without using the nonce"""
        postresponse = self.client.post('/entries/', data={
            'title': 'title this test should fail',
            'description': 'description this test should fail',
            'tags': ['tag2', 'tag3'],
            'interest': 'interest field',
            'get_involved': 'get involved text field',
            'get_involved_url': 'http://example.com/getinvolved',
            'thumbnail_url': 'http://example.com/',
            'content_url': 'http://example.com/',
            'internal_notes': 'Some internal notes'
        })
        self.assertEqual(postresponse.status_code, 400)

    def test_put_bookmark_entry_without_login(self):
        """
        Verify that anonymous users cannot bookmark entries.
        """
        self.client.logout();
        postresponse = self.client.put('/entries/1/bookmark')
        self.assertEqual(postresponse.status_code, 403)

        # verify bookmark count is zero
        entry = Entry.objects.get(id=1)
        bookmarks = entry.bookmarked_by.count()
        self.assertEqual(bookmarks, 0)

    def test_put_bookmark_entry_with_login(self):
        """
        Verify that authenticated users can (un)bookmark an entry.
        """
        postresponse = self.client.put('/entries/1/bookmark')
        self.assertEqual(postresponse.status_code, 204)

        # verify bookmark count is now one
        entry = Entry.objects.get(id=1)
        bookmarks = entry.bookmarked_by.count()
        self.assertEqual(bookmarks, 1)

        # put again, which should clear the bookmark flag for this user
        postresponse = self.client.put('/entries/1/bookmark')
        self.assertEqual(postresponse.status_code, 204)

        # verify bookmark count is now zero
        bookmarks = entry.bookmarked_by.count()
        self.assertEqual(bookmarks, 0)

    def test_bookmarked_entries_view(self):
        """
        Verify that authenticated users can see a list of bookmarks.
        """
        postresponse = self.client.put('/entries/1/bookmark')

        # verify bookmark count is now one
        bookmarkResponse = self.client.get('/entries/bookmarks/')
        self.assertEqual(bookmarkResponse.status_code, 200)

        bookmarkJson = json.loads(str(bookmarkResponse.content, 'utf-8'))
        self.assertEqual(len(bookmarkJson), 1)

class TestMemberEntryView(PulseMemberTestCase):
    def test_approval_requirement(self):
        """
        Verify that entriest submitted by non-Mozilla emails aren't immediately visible
        """
        payload = self.generatePostPayload(data={'title':'title test_approval_requirement'})
        postresponse = self.client.post('/entries/', payload)

        self.assertEqual(postresponse.status_code, 200)

        responseobj = json.loads(str(postresponse.content,'utf-8'))
        entryId = str(responseobj['id'])

        getresponse = self.client.get('/entries/'+ entryId, follow=True)
        getListresponse = json.loads(str(self.client.get('/entries/').content, 'utf-8'))

        self.assertEqual(len(getListresponse['results']), 2)
        self.assertEqual(getresponse.status_code, 404)
