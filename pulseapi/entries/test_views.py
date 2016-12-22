from django.core.urlresolvers import reverse
from django.test import TestCase

from pulseapi.entries.serializers import EntrySerializer
from pulseapi.entries.test_models import EntryFactory


class TestEntryView(TestCase):
    def setUp(self):
        self.entries = [EntryFactory() for i in range(2)]
        for entry in self.entries:
            entry.save()

    def test_get_single_entry_data(self):
        """
        Check if we can get a single entry by its `id`
        """

        id = self.entries[0].id
        response = self.client.get(reverse('entry', kwargs={'pk': id}))
        self.assertEqual(response.status_code, 200)

    def test_post_minimum_entry(self):
        #Entry with minimum amount of content (title, description?)

    def test_post_full_entry(self):
        #Entry with all content

    def test_post_entry_with_mixed_tags(self):
        #Entry with some existing tags, some new tags

    def test_post_entry_with_mixed_creators(self):
        #Entry with some existing creators, some new creators

    def test_get_entries_list(self):
        #Get /entries endpoint

    def test_get_tag_list(self):
        #maybe for another view. But tags list should have multiple tags, some with multiple entries associated
        #do we need an endpoint for /tags/{tagname} that has the associated entries? or does /entries/?tag=foo work?

    def test_get_creator_list(self):
        #same as above, for creators

    def test_entries_search(self):
        #test searching entries

    def test_entries_tags(self):
        #test filtering entries by tag

    def test_entries_issue(self):
        #test filtering entires by issue

    def test_post_entry_new_issue(self):
        #posting an entry with a new Issue should result in an error. Permission denied?

    def test_check_for_issues(self):
        #make sure 5 issues are in the database. Does testing use a "real" database?

    def test_post_authentication_requirement(self):
        #uhhhh how do we do this?

    def test_tag_filtering(self):
        # search tags

    def test_creator_filtering(self):
        # search creators, for autocomplete