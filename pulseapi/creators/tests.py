import json
from urllib.parse import quote
from django.urls import reverse
from django.conf import settings
from django.http.request import HttpRequest
from rest_framework.request import Request

from pulseapi.profiles.models import UserProfile
from pulseapi.users.factory import BasicEmailUserFactory
from pulseapi.creators.serializers import CreatorSerializer
from pulseapi.creators.views import CreatorsPagination
from pulseapi.tests import PulseStaffTestCase


class TestEntryCreatorViews(PulseStaffTestCase):
    def test_get_creator_list_v1(self):
        """Make sure we can get a list of creators for v1"""
        response = self.client.get(reverse('creators-list'))
        page = CreatorsPagination()
        expected_data = CreatorSerializer(
            page.paginate_queryset(
                UserProfile.objects.filter(related_user__is_active=True).order_by('id'),
                request=Request(request=HttpRequest())  # mock request to satisfy the required arguments
            ),
            many=True
        ).data
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(response.data['results'], expected_data)

    def test_get_creator_list_404_for_v2(self):
        """Make sure we get a 404 if we access the creator list using v2"""
        response = self.client.get(reverse(
            'creators-list',
            args=[settings.API_VERSIONS['version_2'] + '/']
        ))
        self.assertEqual(response.status_code, 404)

    def test_creator_filtering(self):
        """search creators, for autocomplete"""
        profile = UserProfile.objects.last()
        # Creating an "active" user account to link to the profile,
        # as we are filtering to show only active profiles in our API views.
        BasicEmailUserFactory(profile=profile, is_active=True)

        response = self.client.get('{creator_url}?name={search}'.format(
            creator_url=reverse('creators-list'),
            search=quote(profile.name)
        ))
        response_creator = json.loads(str(response.content, 'utf-8'))['results'][0]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(profile.id, response_creator['creator_id'])

    def test_creator_filtering_hiding_inactive_users(self):
        """Testing that inactive users are not returned in the creator view"""
        profile = UserProfile.objects.last()
        # Creating an "inactive" user account to link to the profile,
        # as we are filtering to show only active profiles in our API views.
        BasicEmailUserFactory(profile=profile, is_active=False)

        response = self.client.get('{creator_url}?name={search}'.format(
            creator_url=reverse('creators-list'),
            search=quote(profile.name)
        ))
        search_results = json.loads(str(response.content, 'utf-8'))['results']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(search_results, [])
