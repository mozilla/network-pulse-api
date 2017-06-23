import json
from django.test import TestCase
from pulseapi.issues.models import Issue

class TestIssues(TestCase):

    def test_check_for_issues(self):
        issues = self.client.get('/api/pulse/issues/')
        issuesJson = json.loads(str(issues.content, 'utf-8'))
        self.assertEqual(issues.status_code, 200)
        self.assertEqual(len(issuesJson), 5)

        issue_from_api = issuesJson[0]
        self.assertEqual('description' in issue_from_api, True)

        issue_from_db = Issue.objects.get(name=issue_from_api['name'])
        self.assertEqual(issue_from_db['description'], issue_from_api['description'])
