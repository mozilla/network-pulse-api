import json

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client

from pulseapi.users.test_models import EmailUserFactory
from pulseapi.entries.test_models import EntryFactory


class TestEntryView(TestCase):
    def setUp(self):
        self.entries = [EntryFactory() for i in range(2)]
        for entry in self.entries:
            entry.save()

        email = "test@example.org"
        password = "password1234"
        user = EmailUserFactory(email=email, password=password, name="test user")
        user.save()

        self.client = Client()
        self.client.force_login(user);

        values = json.loads(str(self.client.get('/nonce/').content, 'utf-8'))
        # Set up with some curated data for all tests to use
        postresponse = self.client.post('/entries/', data={
            'title': 'title setUp1',
            'description': 'description setUp',
            'nonce': values['nonce'],
            'csrfmiddlewaretoken': values['csrf_token'],
            'creators': 'Pomax',
            'tags': ['tag1', 'tag2'],
            'interest': 'interest field',
            'issues': 'Open Innovation',
            'get_involved': 'get involved text field',
            'get_involved_url': 'http://example.com/getinvolved',
            'thumbnail_url': 'http://example.com/',
            'content_url': 'http://example.com/',
            'internal_notes': 'Some internal notes'
        })

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
        values = json.loads(str(self.client.get('/nonce/').content, 'utf-8'))
        postresponse = self.client.post('/entries/', data={
            'title': 'test entry 1',
            'description': 'description',
            'nonce': values['nonce'],
            'csrfmiddlewaretoken': values['csrf_token'],
            'interest': 'none',
            'get_involved': 'no',
            'get_involved_url': 'http://example.com/',
            'thumbnail_url': 'http://example.com/',
            'content_url': 'http://example.com/',
        })

        self.assertEqual(postresponse.status_code, 200)

    def test_post_duplicate_title(self):
        """Make sure multiple entries can have the same title"""
        values = json.loads(str(self.client.get('/nonce/').content, 'utf-8'))

        postresponse = self.client.post('/entries/', data={
            'title': 'title setUp1',
            'description': 'description new setUp',
            'nonce': values['nonce'],
            'csrfmiddlewaretoken': values['csrf_token'],
            'creators': 'Pomax',
            'tags': ['tag1', 'tag2'],
            'interest': 'interest field',
            'issues': 'Open Innovation',
            'get_involved': 'get involved text field',
            'get_involved_url': 'http://example.com/getinvolved',
            'thumbnail_url': 'http://example.com/',
            'content_url': 'http://example.com/',
            'internal_notes': 'Some internal notes'
        })
        entriesJson = json.loads(str(self.client.get('/entries/').content, 'utf-8'))
        self.assertEqual(postresponse.status_code, 200)
        self.assertEqual(len(entriesJson), 4)

    def test_post_empty_title(self):
        """Make sure entries require a title"""
        values = json.loads(str(self.client.get('/nonce/').content, 'utf-8'))

        postresponse = self.client.post('/entries/', data={
            'title': '',
            'description': 'description empty title',
            'nonce': values['nonce'],
            'csrfmiddlewaretoken': values['csrf_token'],
            'creators': 'Pomax',
            'tags': ['tag1', 'tag2'],
            'interest': 'interest field',
            'issues': 'Open Innovation',
            'get_involved': 'get involved text field',
            'get_involved_url': 'http://example.com/getinvolved',
            'thumbnail_url': 'http://example.com/',
            'content_url': 'http://example.com/',
            'internal_notes': 'Some internal notes'
        })
        self.assertEqual(postresponse.status_code, 400)

    def test_post_empty_description(self):
        """Make sure entries require a description"""
        values = json.loads(str(self.client.get('/nonce/').content, 'utf-8'))

        postresponse = self.client.post('/entries/', data={
            'title': 'title empty description',
            'description': '',
            'nonce': values['nonce'],
            'csrfmiddlewaretoken': values['csrf_token'],
            'creators': 'Pomax',
            'tags': ['tag1', 'tag2'],
            'interest': 'interest field',
            'issues': 'Open Innovation',
            'get_involved': 'get involved text field',
            'get_involved_url': 'http://example.com/getinvolved',
            'thumbnail_url': 'http://example.com/',
            'content_url': 'http://example.com/',
            'internal_notes': 'Some internal notes'
        })
        self.assertEqual(postresponse.status_code, 400)

    def test_post_full_entry(self):
        """Entry with all content"""

        values = json.loads(str(self.client.get('/nonce/').content, 'utf-8'))
        postresponse = self.client.post('/entries/', data={
            'title': 'test full entry',
            'description': 'description full entry',
            'nonce': values['nonce'],
            'csrfmiddlewaretoken': values['csrf_token'],
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
        })
        self.assertEqual(postresponse.status_code, 200)

    def test_post_entry_with_mixed_tags(self):
        """
        Post entries with some existing tags, some new tags
        See if tags endpoint has proper results afterwards
        """
        values = json.loads(str(self.client.get('/nonce/').content, 'utf-8'))
        postresponse = self.client.post('/entries/', data={
            'title': 'title test_post_entry_with_mixed_tags2',
            'description': 'description test_post_entry_with_mixed_tags',
            'nonce': values['nonce'],
            'csrfmiddlewaretoken': values['csrf_token'],
            'tags': ['tag2', 'tag3'],
            'interest': 'interest field',
            'get_involved': 'get involved text field',
            'get_involved_url': 'http://example.com/getinvolved',
            'thumbnail_url': 'http://example.com/',
            'content_url': 'http://example.com/',
            'internal_notes': 'Some internal notes'
        })

        tagList = json.loads(str(self.client.get('/tags/').content, 'utf-8'))
        self.assertEqual(tagList, ['tag1','tag2','tag3'])


    def test_post_entry_with_mixed_creators(self):
        """
        Post entry with some existing creators, some new creators
        See if creators endpoint has proper results afterwards
        """
        values = json.loads(str(self.client.get('/nonce/').content, 'utf-8'))
        postresponse = self.client.post('/entries/', data={
            'title': 'title test_post_entry_with_mixed_tags2',
            'description': 'description test_post_entry_with_mixed_tags',
            'nonce': values['nonce'],
            'csrfmiddlewaretoken': values['csrf_token'],
            'creators': ['Pomax','Alan'],
            'interest': 'interest field',
            'get_involved': 'get involved text field',
            'get_involved_url': 'http://example.com/getinvolved',
            'thumbnail_url': 'http://example.com/',
            'content_url': 'http://example.com/',
            'internal_notes': 'Some internal notes'
        })
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
        self.assertEqual(len(entriesJson), 1)

    def test_entries_search(self):
        """Make sure filtering searches by tag works"""
        searchList = self.client.get('/entries/?tag=tag1')
        entriesJson = json.loads(str(searchList.content, 'utf-8'))
        self.assertEqual(len(entriesJson), 1)


    def test_entries_issue(self):
        """test filtering entires by issue"""
        values = json.loads(str(self.client.get('/nonce/').content, 'utf-8'))
        postresponse = self.client.post('/entries/', data={
            'title': 'title test_entries_issue',
            'description': 'description test_entries_issue',
            'nonce': values['nonce'],
            'csrfmiddlewaretoken': values['csrf_token'],
            'creators': ['Pomax','Alan'],
            'interest': 'interest field',
            'issues': 'Decentralization',
            'get_involved': 'get involved text field',
            'get_involved_url': 'http://example.com/getinvolved',
            'thumbnail_url': 'http://example.com/',
            'content_url': 'http://example.com/',
            'internal_notes': 'Some internal notes'
        })
        searchList = self.client.get('/entries/?issue=Decentralization')
        entriesJson = json.loads(str(searchList.content, 'utf-8'))
        self.assertEqual(len(entriesJson), 1)

    def test_post_entry_new_issue(self):
        """posting an entry with a new Issue should result in an error. Permission denied?"""
        values = json.loads(str(self.client.get('/nonce/').content, 'utf-8'))
        postresponse = self.client.post('/entries/', data={
            'title': 'title test_entries_issue',
            'description': 'description test_entries_issue',
            'nonce': values['nonce'],
            'csrfmiddlewaretoken': values['csrf_token'],
            'creators': ['Pomax','Alan'],
            'interest': 'interest field',
            'issues': 'Privacy',
            'get_involved': 'get involved text field',
            'get_involved_url': 'http://example.com/getinvolved',
            'thumbnail_url': 'http://example.com/',
            'content_url': 'http://example.com/',
            'internal_notes': 'Some internal notes'
        })
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
