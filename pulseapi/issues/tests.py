import json
from django.test import TestCase


class TestIssues(TestCase):

    def test_check_for_issues(self):
        """make sure 5 issues are in the database."""
        issues = self.client.get('/api/pulse/issues/')
        issuesJson = json.loads(str(issues.content, 'utf-8'))
        self.assertEqual(issues.status_code, 200)
        self.assertEqual(len(issuesJson), 5)
