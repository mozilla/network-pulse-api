from pulseapi.entries.models import Entry
from pulseapi.tests import PulseMemberTestCase


def get_full_payload():
    return {
        'title': 'test test_post_full_entry',
        'description': 'description full entry',
        'tags': ['tag1', 'tag2'],
        'interest': 'interest field',
        'get_involved': 'get involved text field',
        'get_involved_url': 'http://example.com/getinvolved',
        'content_url': 'http://example.com/',
        'internal_notes': 'Some internal notes',
        'featured': True,
        'issues': ['Decentralization'],
        'related_creators': [
            {'name': 'Pomax'},
            {'name': 'Alan'}
        ]
    }


class TestMemberEntryView(PulseMemberTestCase):
    def test_base_serializer(self):
        postresponse = self.client.post(
            '/api/pulse/entries/',
            data=self.generatePostPayload(
                data=get_full_payload()
            )
        )

        self.assertEqual(postresponse.status_code, 200)

    def test_base_serializer_without_content_url(self):
        postresponse = self.client.post(
            '/api/pulse/entries/',
            data=self.generatePostPayload(
                data=get_full_payload(),
                exclude=['title']
            )
        )

        self.assertEqual(postresponse.status_code, 400)

    def test_curriculum_serializer(self):
        postresponse = self.client.post(
            '/api/pulse/entries/curriculum/',
            data=self.generatePostPayload(
                data=get_full_payload()
            )
        )

        self.assertEqual(postresponse.status_code, 200)

    def test_curriculum_serializer_without_content_url(self):
        postresponse = self.client.post(
            '/api/pulse/entries/curriculum/',
            data=self.generatePostPayload(
                data=get_full_payload(),
                exclude=['content_url']
            )
        )

        self.assertEqual(postresponse.status_code, 400)

    def test_info_serializer(self):
        postresponse = self.client.post(
            '/api/pulse/entries/info/',
            data=self.generatePostPayload(
                data=get_full_payload()
            )
        )

        self.assertEqual(postresponse.status_code, 200)

    def test_info_serializer_without_content_url(self):
        postresponse = self.client.post(
            '/api/pulse/entries/info/',
            data=self.generatePostPayload(
                data=get_full_payload(),
                exclude=['content_url']
            )
        )

        self.assertEqual(postresponse.status_code, 400)

    def test_news_serializer(self):
        postresponse = self.client.post(
            '/api/pulse/entries/news/',
            data=self.generatePostPayload(
                data=get_full_payload()
            )
        )

        self.assertEqual(postresponse.status_code, 200)

    def test_news_serializer_without_content_url(self):
        postresponse = self.client.post(
            '/api/pulse/entries/news/',
            data=self.generatePostPayload(
                data=get_full_payload(),
                exclude=['content_url']
            )
        )

        self.assertEqual(postresponse.status_code, 400)

    def test_project_serializer(self):
        postresponse = self.client.post(
            '/api/pulse/entries/project/',
            data=self.generatePostPayload(
                data=get_full_payload()
            )
        )

        self.assertEqual(postresponse.status_code, 200)

    def test_project_serializer_without_content_url(self):
        postresponse = self.client.post(
            '/api/pulse/entries/project/',
            data=self.generatePostPayload(
                data=get_full_payload(),
                exclude=['content_url']
            )
        )

        self.assertEqual(postresponse.status_code, 200)

    def test_session_serializer(self):
        postresponse = self.client.post(
            '/api/pulse/entries/session/',
            data=self.generatePostPayload(
                data=get_full_payload()
            )
        )

        self.assertEqual(postresponse.status_code, 200)

    def test_session_serializer_without_content_url(self):
        postresponse = self.client.post(
            '/api/pulse/entries/session/',
            data=self.generatePostPayload(
                data=get_full_payload(),
                exclude=['content_url']
            )
        )

        self.assertEqual(postresponse.status_code, 200)

    def test_session_serializer_without_content_url_with_thumbnail(self):
        payload = get_full_payload()

        payload['thumbnail'] = {
            'name': 'myfile.jpg',
            'base64':
                'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFhAJ/wlseKgAAAABJRU5ErkJggg==',
        }

        postresponse = self.client.post(
            '/api/pulse/entries/session/',
            data=self.generatePostPayload(
                data=payload
            )
        )

        self.assertEqual(postresponse.status_code, 200)

        entry = Entry.objects.last()

        self.assertEqual(str(entry.thumbnail), '')
        self.assertEqual(entry.get_involved, '')
        self.assertEqual(entry.get_involved_url, '')
