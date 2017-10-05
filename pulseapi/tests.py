import json

from django.test import TestCase, Client
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from pulseapi.users.models import EmailUser
from pulseapi.users.test_models import EmailUserFactory
from pulseapi.profiles.test_models import UserProfileFactory
from pulseapi.creators.models import OrderedCreatorRecord
from pulseapi.creators.test_models import CreatorFactory
from pulseapi.entries.models import Entry
from pulseapi.entries.test_models import EntryFactory

from pulseapi.utility.userpermissions import (
    is_staff_address,
    assign_group_policy,
    add_user_to_main_site,
)


def setup_groups():
    staff, created = Group.objects.get_or_create(name='staff')
    content_type = ContentType.objects.get_for_model(Entry)

    permission = Permission.objects.create(
        codename='can_add_entry',
        name='Can Add Entries',
        content_type=content_type
    )
    staff.permissions.add(permission)
    staff.save()

    permission = Permission.objects.create(
        codename='can_change_entry',
        name='Can Change Entries',
        content_type=content_type
    )
    staff.permissions.add(permission)
    staff.save()

    permission = Permission.objects.create(
        codename='can_delete_entry',
        name='Can Delete Entries',
        content_type=content_type
    )
    staff.permissions.add(permission)
    staff.save()


def setup_entries(test, creator_users):
    test.entries = []
    test.creators = []

    for i in range(2):
        entry = EntryFactory()
        entry.save()

        # Create a simple creator that has no profile
        creators = [CreatorFactory()]
        if creator_users and len(creator_users) > i:
            # If we were passed in users, create a creator attached to a user profile
            creators.append(CreatorFactory(profile=creator_users[i].profile))
        for creator in creators:
            creator.save()
            # Connect the creator with the entry
            OrderedCreatorRecord(entry=entry, creator=creator).save()

        test.creators.extend(creators)
        test.entries.append(entry)


def setup_users_with_profiles(test):
    users = []
    profiles = [UserProfileFactory(is_active=True) for i in range(3)]
    for profile in profiles:
        profile.save()
        user = EmailUserFactory(profile=profile)
        user.save()
        users.append(user)

    test.users_with_profiles = users


def create_logged_in_user(test, name, email, password="password1234"):
    test.name = name

    # create use instance
    User = EmailUser
    user = User.objects.create_user(name=name, email=email, password=password)
    user.save()

    # make sure this user is in the staff group, too
    if is_staff_address(email):
        assign_group_policy(user, "staff")
        add_user_to_main_site(user)

    # log this user in for further testing purposes
    test.user = user
    test.client = Client()
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

    return payload


def boostrap(test, name, email):
    setup_groups()
    create_logged_in_user(
        test,
        name=name,
        email=email
    )
    setup_users_with_profiles(test)
    setup_entries(test, creator_users=test.users_with_profiles)


class PulseMemberTestCase(TestCase):
    """
    A test case wrapper for "plain users" without any staff or admin rights
    """
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
    def setUp(self):
        boostrap(
            self,
            name="staff user",
            email="test@mozilla.org"
        )

    def generatePostPayload(self, data={}):
        return generate_payload(self, data)
