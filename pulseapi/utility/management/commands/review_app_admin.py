"""
Management command called during Heroku Review App post-deployment phase: create an admin user and
post the credentials on a private channel on Slack.
"""
import re

import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from factory import Faker

from pulseapi.users.models import EmailUser


class Command(BaseCommand):
    help = 'Create a superuser for use on Heroku review apps'

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
            m = re.search(r'\d+', reviewapp_name)
            pr_number = m.group()

            # Get PR's title from Github
            token = settings.GITHUB_TOKEN
            org = 'mozilla'
            repo = 'network-pulse-api'
            r = requests.get(f'https://api.github.com/repos/{org}/{repo}/pulls/{pr_number}&access_token={token}')
            try:
                pr_title = ': ' + r.json()['title']
            except KeyError:
                pr_title = ''

            if r.json()['labels']:
                for l in r.json()['labels']:
                    if l['name'] == 'dependencies':
                        color = '#BA55D3'
                        break
                    else:
                        color = '#7CD197'
            else:
                color = '#7CD197'

            slack_payload = {
                'attachments': [
                    {
                        'fallback': 'New review app deployed: It will be ready in a minute!\n'
                                    f'PR {pr_number}{pr_title}\n'
                                    f'Login: admin@mozillafoundation.org\n'
                                    f'Password: {password}\n'
                                    f'URL: https://{reviewapp_name}.herokuapp.com',
                        'pretext':  'New review app deployed. It will be ready in a minute!',
                        'title':    f'PR {pr_number}{pr_title}\n',
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
                                'text': 'View PR on Github',
                                'url': f'https://github.com/mozilla/network-pulse-api/pull/{pr_number}'
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
            print('Done!')
