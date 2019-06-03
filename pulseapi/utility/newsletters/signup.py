from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import JSONParser
from rest_framework import status, permissions
from django.conf import settings
from datetime import datetime

import boto3
import logging
import json


class SQSProxy:
    """
    We use a proxy class to make sure that code that
    relies on SQS posting still works, even when there
    is no "real" sqs client available to work with.
    """

    def send_message(self, QueueUrl, MessageBody):
        """
        As a proxy function, the only thing we report
        is that "things succeeded!" even though nothing
        actually happened.
        """

        return {
            'MessageId': True
        }


# Basket/Salesforce SQS client - Proxy first...
crm_sqs = {
    'client': SQSProxy()
}

# But if there's an SQS access key, bind a "real client".
if settings.CRM_AWS_SQS_ACCESS_KEY_ID:
    crm_sqs['client'] = boto3.client(
        'sqs',
        region_name=settings.CRM_AWS_SQS_REGION,
        aws_access_key_id=settings.CRM_AWS_SQS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.CRM_AWS_SQS_SECRET_ACCESS_KEY,
    )


# sqs destination for salesforce
crm_queue_url = settings.CRM_PETITION_SQS_QUEUE_URL

logger = logging.getLogger(__name__)


@api_view(['POST'])
@parser_classes((JSONParser,))
@permission_classes((permissions.AllowAny,))
def signup_submission_view(request):

    for parameter in ('email', 'source'):
        if parameter not in request.data:
            return Response(
                {'error': f'Missing {parameter} parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )

    data = {
        "email": request.data['email'],
        "lang": "en",
        "format": "html",
        "source_url": request.data['source'],
        "newsletters": 'mozilla-foundation',
    }

    message = json.dumps({
        'app': settings.HEROKU_APP_NAME,
        'timestamp': datetime.now().isoformat(),
        'data': {
            'json': True,
            'form': data,
            'event_type': 'newsletter_signup_data'
        }
    })

    return send_to_sqs(crm_sqs['client'], crm_queue_url, message)


def send_to_sqs(sqs, queue_url, message, type='signup'):
    if settings.DEBUG is True:
        logger.info(f'Sending {type} message: {message}')

    if queue_url is None:
        logger.warning(f'{type} was not submitted: No {type} SQS url was specified')
        return Response({'message': 'success'}, 201)

    try:
        response = sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=message
        )
    except Exception as error:
        logger.error(f'Failed to send {type} with: {error}')
        return Response(
            {'error': f'Failed to queue up {type}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    if 'MessageId' in response and response['MessageId']:
        return Response({'message': 'success'}, 201)
    else:
        return Response(
            {'error': f'Something went wrong with {type}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
