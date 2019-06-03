import json

from django.test import TestCase
from django.core.urlresolvers import reverse


class TestNewsletterSignup(TestCase):

    def test_newsletter_signup(self):
        """
        Check that the signup url exists, and does not support GET
        """
        response = self.client.get(reverse('newsletter-signup'))
        self.assertEqual(response.status_code, 405)

    def test_bad_news_letter_post_missing_content_type(self):
        # wrong media type (missing content_type)
        payload = {
            'email': 'test@example.com',
            'source': 'http://test.example.com/',
        }
        response = self.client.post(reverse('newsletter-signup'), payload)
        self.assertEqual(response.status_code, 415)

    def test_bad_news_letter_post_missing_data(self):
        # missing email
        payload = json.dumps({'source': 'http://test.example.com'})
        response = self.client.post(reverse('newsletter-signup'), payload, content_type='application/json')
        self.assertEqual(response.status_code, 400)

        # missing source
        payload = json.dumps({'email': 'test@example.com'})
        response = self.client.post(reverse('newsletter-signup'), payload, content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_proper_news_letter_post(self):
        payload = json.dumps({
            'email': 'test@example.com',
            'source': 'http://test.example.com/',
        })

        response = self.client.post(reverse('newsletter-signup'), payload, content_type='application/json')

        self.assertEqual(response.status_code, 201)
