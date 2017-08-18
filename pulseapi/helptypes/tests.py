import json
from django.test import TestCase
from .models import HelpType


class TestIssues(TestCase):

    def test_check_for_help_types(self):
        help_types = self.client.get('/api/pulse/helptypes/')
        help_type_json = json.loads(str(help_types.content, 'utf-8'))
        self.assertEqual(help_types.status_code, 200)
        self.assertEqual(len(help_type_json), 13)

        help_type_from_api = help_type_json[0]
        self.assertEqual('description' in help_type_from_api, True)

        help_type_from_db = HelpType.objects.get(name=help_type_from_api['name'])
        self.assertEqual(help_type_from_db.description, help_type_from_api['description'])
