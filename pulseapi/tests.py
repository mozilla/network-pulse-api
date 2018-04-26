import json

from django.test import TestCase, Client, RequestFactory
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group, Permission
from rest_framework import exceptions

from pulseapi.settings import API_VERSION_LIST
from pulseapi.users.models import EmailUser
from pulseapi.users.factory import BasicEmailUserFactory
from pulseapi.profiles.factory import BasicUserProfileFactory
from pulseapi.creators.factory import EntryCreatorFactory
from pulseapi.entries.factory import EntryFactory
from pulseapi.versioning import PulseAPIVersioning

from pulseapi.utility.userpermissions import (
    is_staff_address,
    assign_group_policy,
    add_user_to_main_site,
)


CONTENT_TYPE_JSON = 'application/json'


def setup_groups():
    staff, created = Group.objects.get_or_create(name='staff')
    moderator, created = Group.objects.get_or_create(name='moderator')

    add_entry = Permission.objects.get(codename='add_entry')
    change_entry = Permission.objects.get(codename='change_entry')
    delete_entry = Permission.objects.get(codename='delete_entry')

    staff.permissions.add(add_entry, change_entry, delete_entry)
    staff.save()

    moderator.permissions.add(add_entry, change_entry, delete_entry)
    moderator.save()


def setup_entries(test, creator_users):
    test.entries = []
    test.creators = []

    for i in range(2):
        entry = EntryFactory()
        entry.save()

        creators = [BasicUserProfileFactory(use_custom_name=True)]
        if creator_users and len(creator_users) > i:
            # If we were passed in users, create a creator attached to a user profile
            for user in creator_users:
                creators.append(user.profile)
        for creator in creators:
            creator.save()
            # Connect the creator with the entry
            EntryCreatorFactory(entry=entry, profile=creator)

        test.creators.extend(creators)
        test.entries.append(entry)


def setup_users_with_profiles(test):
    users = []
    profiles = [
        BasicUserProfileFactory(active=True, use_custom_name=(i % 2 == 0))
        for i in range(3)
    ]
    for profile in profiles:
        user = BasicEmailUserFactory(profile=profile)
        users.append(user)

    test.users_with_profiles = users


class JSONDefaultClient(Client):
    """
    Same as a regular test client except the default content type is 'application/json'
    for the post method instead of 'multipart/form-data'
    """
    def post(self, path, data=None, content_type=CONTENT_TYPE_JSON,
             follow=False, secure=False, **extra):
        return super(JSONDefaultClient, self).post(
            path,
            data=data,
            content_type=content_type,
            follow=follow,
            secure=secure,
            **extra
        )

    def put(self, path, data=None, content_type=CONTENT_TYPE_JSON,
            follow=False, secure=False, **extra):
        return super(JSONDefaultClient, self).put(
            path,
            data=data,
            content_type=content_type,
            follow=follow,
            secure=secure,
            **extra
        )


def create_logged_in_user(test, name, email, password="password1234", is_moderator=False):
    test.name = name

    # create use instance
    User = EmailUser
    user = User.objects.create_user(name=name, email=email, password=password)
    user.save()

    # make sure this user is in the staff group, too
    if is_staff_address(email):
        assign_group_policy(user, "staff")
        add_user_to_main_site(user)

    if is_moderator:
        assign_group_policy(user, "moderator")

    # log this user in for further testing purposes
    test.user = user
    test.client = JSONDefaultClient()
    test.client.force_login(user)


def generate_default_payload(values):
    return {
        'title': 'default title',
        'nonce': values['nonce'],
        'csrfmiddlewaretoken': values['csrf_token'],
        'content_url': 'http://example.com/',
        'tags': ['tag1', 'tag2']
    }


def generate_payload(test, data={}, payload=False):
    values = json.loads(
        str(test.client.get('/api/pulse/nonce/').content, 'utf-8')
    )

    if payload is False:
        payload = generate_default_payload(values)

    for key in data:
        payload[key] = data[key]

    return json.dumps(payload)


def boostrap(test, name, email, is_moderator=False):
    setup_groups()
    create_logged_in_user(
        test,
        name=name,
        email=email,
        is_moderator=is_moderator
    )
    setup_users_with_profiles(test)
    setup_entries(test, creator_users=test.users_with_profiles)


class PulseMemberTestCase(TestCase):
    """
    A test case wrapper for "plain users" without any staff or admin rights
    """
    maxDiff = None

    def setUp(self):
        boostrap(
            self,
            name="plain user",
            email="test@example.org"
        )

    def generatePostPayload(self, data={}):
        return generate_payload(self, data)


class PulseStaffTestCase(TestCase):
    """
    A test case wrapper for "staff" users, due to having a mozilla login
    """
    maxDiff = None

    def setUp(self):
        boostrap(
            self,
            name="staff user",
            email="test@mozilla.org"
        )

    def generatePostPayload(self, data={}):
        return generate_payload(self, data)


class PulseModeratorTestCase(TestCase):
    """
    A test case wrapper for "moderator" users
    """
    def setUp(self):
        boostrap(
            self,
            name="Moderator user",
            email="moderator@example.org",
            is_moderator=True
        )

    def generatePostPayload(self, data={}):
        return generate_payload(self, data)


class TestAPIVersioning(TestCase):
    """
    Test API versioning
    """
    def setUp(self):
        self.client = JSONDefaultClient()
        self.factory = RequestFactory()
        self.version_scheme = PulseAPIVersioning()

    def test_status_route(self):
        response = self.client.get(reverse('api-status'))
        status = json.loads(str(response.content, 'utf-8'))

        self.assertDictEqual(status, {
            'latestApiVersion': API_VERSION_LIST[-1][1],
        })

    def test_versioning_scheme_default_version(self):
        request = self.factory.get(reverse('api-status'))
        version = self.version_scheme.determine_version(request, version=None)

        self.assertEqual(version, self.version_scheme.default_version)

    def test_invalid_version(self):
        request = self.factory.get(reverse('entries-list'))

        with self.assertRaises(exceptions.NotFound) as context_manager:
            self.version_scheme.determine_version(request, version='v100')

        self.assertEqual(context_manager.exception.detail, self.version_scheme.invalid_version_message)
