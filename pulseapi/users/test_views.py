from django.core.urlresolvers import reverse
from django.test import TestCase

from pulseapi.users.serializers import EmailUserSerializer
from pulseapi.users.test_models import EmailUserFactory


class TestUserView(TestCase):
    def setUp(self):
        self.users = [EmailUserFactory() for i in range(2)]
        for user in self.users:
            user.save()

    # def test_list_users_returns_user_data(self):
    #     """
    #     Check if we can get a list of users
    #     """
    #     response = self.client.get(reverse('user-list'))

    #     user_data = json.loads(response.content.decode('utf-8'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(
    #         len(user_data['results']),
    #         len(self.users)
    #     )
    #     for user in self.users:
    #         user_serializer = UserWithDetailsSerializer(
    #             user,
    #             context={'request': response.wsgi_request}
    #         )
    #         self.assertIn(
    #             user_serializer.data,
    #             user_data['results']
    #         )

    # def test_get_single_user_data(self):
    #     """
    #     Check if we can get a single user by its `id`
    #     """

    #     id = self.users[0].id
    #     response = self.client.get(reverse('user', kwargs={'pk': id}))
    #     self.assertEqual(response.status_code, 200)
