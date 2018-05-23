"""Store contribution activities for a list of github repos"""

import attr
import csv
import io
from datetime import datetime, timezone, timedelta
import requests
from requests.packages.urllib3.exceptions import MaxRetryError
import boto3
from pathlib import Path

from django.conf import settings

token = settings.GITHUB_TOKEN

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


# Rate limit exception
class RateLimitExceptionError(Exception):
    """
    Exception raised when the API rate limit is reached.
    """

    pass


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


# Get the list of repos we need contribution data from
def get_repo_list():
    with open(Path(settings.BASE_DIR + '/global_sprint_repo_list.txt')) as f:
        return [l.rstrip() for l in f]


# Check if the data was updated in the last two hours. If not, alert.
def is_stale():
    data = s3.get_object(
        Bucket=settings.GLOBAL_SPRINT_S3_BUCKET,
        Key=s3_data_path.as_posix(),
    )
    now = datetime.now(tz=timezone.utc)
    time_diff = now - data['LastModified']

    if time_diff >= timedelta(hours=2):
        payload = {
            "message_type": "CRITICAL",
            "entity_id": "GlobalSprintContributionData",
            "entity_display_name": f"Global Sprint scheduled task failed: 'global-sprint-github-event-data.csv'"
                                   f" was not updated for {time_diff}",
            "state_message": f"The scheduled task in charge of aggregating contributions data for the Global Sprint "
                             f"failed: 'global-sprint-github-event-data.csv' was not updated for {time_diff}.\n"
                             f"The task is running on network-api-pulse app ('clock' process). The file is "
                             f"on S3 under mofo-projects, in the global-sprint-2018-data bucket. Logs "
                             f"are available on Logentries: "
                             f"https://eu.logentries.com/app/3aae5f3f#/search/log/ad178cbf?last=Last%2020%20Minutes."
        }
        requests.post(f"https://alert.victorops.com/integrations/generic/20131114/alert/{settings.VICTOROPS_KEY}",
                      json=payload)
        print(f"Failure: the file was not updated for {time_diff}. An alert has been sent.")


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


def create_events_csv(repos):
    rows = []
    repo_error = []

    session = requests.Session()
    adapter = requests.adapters.HTTPAdapter(max_retries=3)
    session.mount('https://', adapter)

    try:
        for repo in repos:
            print(f'Fetching Activity for: {repo}')
            for page in range(1, 11):
                try:
                    r = session.get(f'https://api.github.com/repos/{repo}/events?page={page}&access_token={token}')
                    try:
                        if int(r.headers['X-RateLimit-Remaining']) == 0:
                            raise RateLimitExceptionError
                    except KeyError as e:
                        print(f"Response from Github API for {repo} did not contain the X-RateLimit-Remaining header. "
                              "Continuing execution as if it were present...")
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
    except RateLimitExceptionError:
        print(f"Warning! Github API's rate limit reached while doing a request to {repo} at page {page}. "
              f"The contribution file will be partially updated.")

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
        # Check if the file was recently updated or alert
        is_stale()

        print('Generating the repositories\' list')
        repos = get_repo_list()

        print('Downloading GitHub event data from S3')
        saved_data = download_existing_data()

        print('Fetching most recent GitHub events')
        new_data = create_events_csv(repos)

        print('Merging and de-duplicating events')
        upload_data = update_events_csv(saved_data, new_data)

        print('Uploading event data to S3')
        upload_updated_data(upload_data)

        print('Success!')
    else:
        print('GLOBAL_SPRINT_ENABLED must be set to True to run this task.')
