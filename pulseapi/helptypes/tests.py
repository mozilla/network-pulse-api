import json
from django.test import TestCase
from .models import Issue

class TestIssues(TestCase):

    def test_check_for_help_types(self):
        issues = self.client.get('/api/pulse/helptypes/')
        issuesJson = json.loads(str(issues.content, 'utf-8'))
        self.assertEqual(issues.status_code, 200)
        self.assertEqual(len(issuesJson), 12)

        help_type_from_api = issuesJson[0]
        self.assertEqual('description' in help_type_from_api, True)

        issue_from_db = Issue.objects.get(name=help_type_from_api['name'])
        self.assertEqual(issue_from_db.description, help_type_from_api['description'])
