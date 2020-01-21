"""
Management command called during Heroku Review App post-deployment phase: create an admin user and
post the credentials on a private channel on Slack.
"""
import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from factory import Faker

from pulseapi.users.models import EmailUser


class Command(BaseCommand):
    help = 'Create a superuser to use on Heroku review apps'

    def handle(self, *args, **options):
        try:
            EmailUser.objects.get(email='admin@mozillafoundation.org')
            print('superuser already exists')
        except ObjectDoesNotExist:
            password = Faker(
                'password',
                length=16,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True
            ).generate({})
            EmailUser.objects.create_superuser('admin', 'admin@mozillafoundation.org', password)

            reviewapp_name = settings.HEROKU_APP_NAME
            pr_number = settings.HEROKU_PR_NUMBER
            branch_name = settings.HEROKU_BRANCH

            # As of 01/2020 we can only get the PR number if the review app was automatically created
            # (https://devcenter.heroku.com/articles/github-integration-review-apps#injected-environment-variables).
            # For review app manually created, we have to use the branch name instead.
            if pr_number:
                # Get PR's title from Github
                token = settings.GITHUB_TOKEN
                org = 'mozilla'
                repo = 'network-pulse-api'
                r = requests.get(f'https://api.github.com/repos/{org}/{repo}/pulls/{pr_number}&access_token={token}')
                try:
                    pr_title = ': ' + r.json()['title']
                except KeyError:
                    pr_title = ''

                for l in r.json()['labels']:
                    if l['name'] == 'dependencies':
                        color = '#BA55D3'
                        break
                else:
                    color = '#7CD197'
                fallback_text = f'''New review app deployed: It will be ready in a minute!\n
                                                PR {pr_number}{pr_title}\n
                                                Login: admin\n
                                                Password: {password}\n
                                                URL: https://{reviewapp_name}.herokuapp.com'''
                message_title = f'PR {pr_number}{pr_title}\n'
                github_url = f'https://github.com/mozilla/network-pulse-api/pull/{pr_number}'
                github_button_text = 'View PR on Github'

            else:
                color = '#7CD197'
                fallback_text = f'''New review app deployed: It will be ready in a minute!\n
                                                Branch: {branch_name}\n
                                                Login: admin\n
                                                Password: {password}\n
                                                URL: https://{reviewapp_name}.herokuapp.com'''
                message_title = f'Branch: {branch_name}\n'
                github_url = f'https://github.com/mozilla/network-pulse-api/tree/{branch_name}'
                github_button_text = 'View branch on Github'

            slack_payload = {
                'attachments': [
                    {
                        'fallback': f'{fallback_text}',
                        'pretext':  'New review app deployed. It will be ready in a minute!',
                        'title':    f'{message_title}',
                        'text':     'Login: admin@mozillafoundation.org\n'
                                    f'Password: {password}\n',
                        'color':    f'{color}',
                        'actions': [
                            {
                                'type': 'button',
                                'text': 'View review app',
                                'url': f'https://{reviewapp_name}.herokuapp.com'
                            },
                            {
                                'type': 'button',
                                'text': f'{github_button_text}',
                                'url': f'{github_url}'
                            }
                        ]
                    }
                ]
            }

            slack_webhook = settings.SLACK_WEBHOOK_RA
            r = requests.post(f'{slack_webhook}',
                              json=slack_payload,
                              headers={'Content-Type': 'application/json'}
                              )

            # Raise if post request was a 4xx or 5xx
            r.raise_for_status()
            print('Superuser created!')
