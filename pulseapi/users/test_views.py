import json

from pulseapi.tests import PulseMemberTestCase


class TestUserViews(PulseMemberTestCase):
    def test_nonce_403_for_unauthenticated_user(self):
        """
        Assert that an unauthenticated user calling /nonce is a 403
        """
        self.client.logout()
        values = self.client.get('/api/pulse/nonce/')
        self.assertEqual(values.status_code, 403)

    def test_nonce_for_authenticated_user(self):
        """
        Assert that an unauthenticated user calling /nonce is a 403
        """
        response = self.client.get('/api/pulse/nonce/')
        self.assertEqual(response.status_code, 200)
        string = response.content.decode('utf-8')
        json.loads(string)

    def test_user_status_false(self):
        """
        Assert that an unauthenticated user calling /userstatus is 200
        with response { loggedin: false }
        """
        self.client.logout()
        response = self.client.get('/api/pulse/userstatus/')
        self.assertEqual(response.status_code, 200)

        string = response.content.decode('utf-8')
        json_obj = json.loads(string)
        self.assertEqual(json_obj['loggedin'], False)

    def test_user_status_true(self):
        """
        Assert that an authenticated user calling /userstatus is 200
        with response { loggedin: true, username: "...", email: "...", profileid: "..." }
        """
        response = self.client.get('/api/pulse/userstatus/')
        self.assertEqual(response.status_code, 200)

        string = response.content.decode('utf-8')
        json_obj = json.loads(string)
        self.assertEqual(json_obj['loggedin'], True)
        self.assertEqual(json_obj['email'], 'test@example.org')
        self.assertEqual(json_obj['profileid'], '1')
        self.assertEqual(json_obj['username'], 'plain user')
