"""Store contribution activities for a list of github repos"""

import attr
import csv
import io
from datetime import datetime
import requests
from requests.packages.urllib3.exceptions import MaxRetryError
import boto3
from pathlib import Path

from django.conf import settings

token = settings.GITHUB_TOKEN
repos = settings.GLOBAL_SPRINT_REPO_LIST
s3 = None
s3_data_path = ''
local_data_path = 'existing_events.csv'
local_new_data_path = 'new_events.csv'

if settings.GLOBAL_SPRINT_ENABLED:
    bucket_path = Path(settings.GLOBAL_SPRINT_S3_ENVIRONMENT)
    s3_data_path = bucket_path / 'global-sprint-github-event-data.csv'

    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.GLOBAL_SPRINT_AWS_ACCESS_KEY,
        aws_secret_access_key=settings.GLOBAL_SPRINT_AWS_SECRET_ACCESS_KEY
    )


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
    repo_error = []

    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=3)
    session.mount('https://', adapter)

    for repo in repos:
        print(f'Fetching Activity for: {repo}')
        for page in range(1, 11):
            try:
                r = session.get(f'https://api.github.com/repos/{repo}/events?page={page}&access_token={token}')
            except MaxRetryError as err:
                print(f"Request made to Github API for {repo} failed. Error message: {err}")
                repo_error.append(repo)
                break
            try:
                extracted_data = extract_data(r.json())

                for event in extracted_data:
                    row = [event.id, event.created_at, event.type, event.action, event.contributor, event.repo]
                    rows.append(row)
            except TypeError:
                print(f"Couldn't process request made to {repo}. Request status: {r.status_code}")
                repo_error.append(repo)
                break

    if repo_error:
        print(f"Warning! List of repo(s) that encountered an error during this run: {', '.join(repo_error)}")

    new_data = io.StringIO()
    csvwriter = csv.writer(
        new_data,
        delimiter=',',
        quotechar='|',
        quoting=csv.QUOTE_MINIMAL
    )
    csvwriter.writerows(rows)
    return new_data.getvalue()


def update_events_csv(saved_data, new_data):
    previous_events = csv.reader(io.StringIO(saved_data))
    new_events = csv.reader(io.StringIO(new_data))
    to_write = set(tuple(r) for r in new_events) | set(tuple(r) for r in previous_events)

    upload_data = io.StringIO()
    csvwriter = csv.writer(
        upload_data,
        delimiter=',',
        quotechar='|',
        quoting=csv.QUOTE_MINIMAL
    )
    csvwriter.writerows(sorted(to_write))

    value = upload_data.getvalue()

    return value.encode()


def download_existing_data():
    saved_data = io.BytesIO()
    s3.download_fileobj(
        settings.GLOBAL_SPRINT_S3_BUCKET,
        s3_data_path.as_posix(),
        saved_data
    )
    return saved_data.getvalue().decode("utf-8")


def upload_updated_data(upload_data):
    bio = io.BytesIO(upload_data)
    return s3.upload_fileobj(
        bio,
        settings.GLOBAL_SPRINT_S3_BUCKET,
        s3_data_path.as_posix()
    )


def run():
    if settings.GLOBAL_SPRINT_ENABLED:
        print('Downloading GitHub event data from S3')
        saved_data = download_existing_data()

        print('Fetching most recent GitHub events')
        new_data = create_events_csv()

        print('Merging and de-duplicating events')
        upload_data = update_events_csv(saved_data, new_data)

        print('Uploading event data to S3')
        upload_updated_data(upload_data)
    else:
        print('GLOBAL_SPRINT_ENABLED must be set to True to run this task.')
