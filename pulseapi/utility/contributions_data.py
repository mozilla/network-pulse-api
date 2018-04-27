"""Store contribution activities for a list of github repos"""

import attr
import csv
from datetime import datetime
import requests
import boto3
from os import path

from django.conf import settings

token = settings.GITHUB_TOKEN
repos = settings.GLOBAL_SPRINT_REPO_LIST
s3 = None
s3_data_path = ''
local_data_path = 'existing_events.csv'
local_new_data_path = 'new_events.csv'

if settings.USE_S3:
    s3_data_path = path.join(settings.AWS_LOCATION, 'global-sprint-github-event-data.csv')
    s3 = boto3.client('s3')


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

    with open(local_new_data_path, 'w', newline='') as csvfile:
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


def download_existing_data():
    s3.download_file(
        settings.AWS_STORAGE_BUCKET_NAME,
        s3_data_path,
        local_data_path
    )


def upload_updated_data():
    with open(local_data_path, 'rb') as file:
        s3.upload_fileobj(
            file,
            settings.AWS_STORAGE_BUCKET_NAME,
            s3_data_path
        )


def run():
    if settings.USE_S3:
        # Download the existing github event data
        download_existing_data()
        # Create a csv containing latest github events
        create_events_csv()
        # Update the existing github event data with the latest events
        update_events_csv(local_data_path, local_new_data_path)
        # Upload the updated github event data
        upload_updated_data()
    else:
        print('S3 access not given. Please provide the appropriate S3 environment variables.')
