"""Store contribution activities for a list of github repos"""

import attr
import csv
from datetime import datetime
import requests

from pulseapi import settings

token = settings.GITHUB_TOKEN

# Move this list to an env var
repos = ['mozilla/foundation.mozilla.org', 'mozilla/network-pulse-api']


@attr.s
class GithubEvent(object):
    id = attr.ib()
    # Issues, comments, pushes, etc
    type = attr.ib()
    # Open, close, reopen, etc
    action = attr.ib()
    created_at = attr.ib()
    contributor = attr.ib()
    repo = attr.ib()


# Parse a json file to only keep what we need
def extract_data(json_data):
    result = []

    for event in json_data:
        time = datetime.strptime(event['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        if 'action' in event['payload']:
            action = event['payload']['action']
        else:
            action = ""
        result.append(GithubEvent(
            id=event['id'],
            created_at=time,
            type=event['type'],
            action=action,
            contributor=event['actor']['login'],
            repo=event['repo']['name'],
            ))

    return result


def create_events_csv():
    rows = []

    for repo in repos:
        for page in range(1, 11):
            r = requests.get(f'https://api.github.com/repos/{repo}/events?page={page}&access_token={token}')
            extracted_data = extract_data(r.json())

            for event in extracted_data:
                row = [event.id, event.created_at, event.type, event.action, event.contributor, event.repo]
                rows.append(row)

    with open('new_events.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(
            csvfile,
            delimiter=',',
            quotechar='|',
            quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerows(rows)


def update_events_csv(original_csv_path, new_events_csv_path):
    with open(original_csv_path, newline='') as original_csv_file,\
            open(new_events_csv_path, newline='') as new_events_csv_file:
        previous_events = csv.reader(original_csv_file)
        new_events = csv.reader(new_events_csv_file)
        to_write = set(tuple(r) for r in new_events) | set(tuple(r) for r in previous_events)

    with open(original_csv_path, 'w', newline='') as original_csv_file:
        csvwriter = csv.writer(
            original_csv_file,
            delimiter=',',
            quotechar='|',
            quoting=csv.QUOTE_MINIMAL)
        csvwriter.writerows(sorted(to_write))


def main():
    # Create a csv containing latest github events
    create_events_csv()
