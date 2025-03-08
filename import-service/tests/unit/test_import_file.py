import json
import sys
import os
import pytest
from moto import mock_aws
import boto3
from botocore.exceptions import ClientError
import json

# Import your Lambda function
# Add the lambda directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'lambda')))
from import_file import handler as lambda_handler

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['BUCKET_NAME'] = 'test_bucket'

@pytest.fixture
def s3_client(aws_credentials):
    with mock_aws():
        yield boto3.client('s3', region_name='us-east-1')

def test_lambda_handler_success(s3_client):
    # Set up test data
    bucket_name = os.environ['BUCKET_NAME']
    object_key = 'test-object.csv'
    s3_client.create_bucket(Bucket=bucket_name)

    # Mock the event input
    event = {
        'queryStringParameters': {
            'name': object_key
        }
    }

    # Call the Lambda function
    response = lambda_handler(event, None)

    # Assert the response
    assert response['statusCode'] == 200
    body = response['body']
    assert body.startswith('https://')
