from io import StringIO

from django.test import TestCase
from django.core.management import call_command

from pulseapi.entries.models import Entry
from pulseapi.creators.models import EntryCreator
from pulseapi.profiles.models import UserBookmarks, UserProfile
from pulseapi.tags.models import Tag
from pulseapi.users.models import EmailUser

models = [
    EntryCreator,
    Entry,
    UserBookmarks,
    UserProfile,
    Tag,
    EmailUser,
]

out = StringIO()


class TestLoadFakeData(TestCase):

    def test_it_finishes_and_creates_data(self):
        call_command("load_fake_data", stdout=out)

        self.assertIn('Done!', out.getvalue())

        for m in models:
            self.assertTrue(m.objects.all())


class TestFlushData(TestCase):

    def test_all_models_data_is_deleted(self):
        call_command("flush_data", stdout=out)

        self.assertIn('Done!', out.getvalue())

        for m in models:
            self.assertFalse(m.objects.all())
