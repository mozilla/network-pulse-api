import json

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client

from pulseapi.users.test_models import EmailUserFactory
from pulseapi.entries.test_models import EntryFactory
from pulseapi.entries.models import Entry


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
            'title': 'title test_post_entry_with_mixed_tags1',
            'description': 'description test_post_entry_with_mixed_tags',
            'nonce': values['nonce'],
            'csrfmiddlewaretoken': values['csrf_token'],
            'tags': ['tag1', 'tag2'],
            'interest': 'interest field',
            'get_involved': 'get involved text field',
            'get_involved_url': 'http://example.com/getinvolved',
            'thumbnail_url': 'http://example.com/',
            'content_url': 'http://example.com/',
            'internal_notes': 'Some internal notes'
        })
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
        Post entries with some existing creators, some new creators
        See if creators endpoint has proper results afterwards
        """
        values = json.loads(str(self.client.get('/nonce/').content, 'utf-8'))
        postresponse = self.client.post('/entries/', data={
            'title': 'title test_post_entry_with_mixed_tags1',
            'description': 'description test_post_entry_with_mixed_tags',
            'nonce': values['nonce'],
            'csrfmiddlewaretoken': values['csrf_token'],
            'creators': 'Pomax',
            'interest': 'interest field',
            'get_involved': 'get involved text field',
            'get_involved_url': 'http://example.com/getinvolved',
            'thumbnail_url': 'http://example.com/',
            'content_url': 'http://example.com/',
            'internal_notes': 'Some internal notes'
        })
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

    # def test_get_entries_list(self):
    #     #Get /entries endpoint

    def test_get_tag_list(self):
        tagList = self.client.get('/tags/')
        self.assertEqual(tagList.status_code, 200)

    def test_get_creator_list(self):
        creatorList = self.client.get('/creators/')
        self.assertEqual(creatorList.status_code, 200)

    # def test_entries_search(self):
    #     #test searching entries

    # def test_entries_tags(self):
    #     #test filtering entries by tag

    # def test_entries_issue(self):
    #     #test filtering entires by issue

    # def test_post_entry_new_issue(self):
    #     #posting an entry with a new Issue should result in an error. Permission denied?

    # def test_check_for_issues(self):
    #     #make sure 5 issues are in the database. Does testing use a "real" database?

    # def test_post_authentication_requirement(self):
    #     #uhhhh how do we do this?

    # def test_tag_filtering(self):
    #     # search tags

    # def test_creator_filtering(self):
    #     # search creators, for autocomplete