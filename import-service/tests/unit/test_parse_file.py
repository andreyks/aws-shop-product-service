import pytest
import boto3
from moto import mock_aws
import sys
import os

# Import your Lambda function
# Add the lambda directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'lambda')))
from parse_file import handler as lambda_handler


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    import os
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['BUCKET_NAME'] = 'test_bucket'

@pytest.fixture
def s3_client(aws_credentials):
    with mock_aws():
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket=os.environ['BUCKET_NAME'])
        s3.put_object(Bucket=os.environ['BUCKET_NAME'], Key='prefix/test-file.txt', Body='Test content')
        yield s3



def test_lambda_handler(s3_client):
    event = {
        'Records': [{
            'eventName': 'ObjectCreated:Put',
            's3': {
                'bucket': {'name': 'test-bucket'},
                'object': {'key': 'uploaded/test-file.csv'}
            }
        }]
    }
    context = {}
    
    response = lambda_handler(event, context)
    
    # Add assertions here to check if your Lambda function behaved correctly
    assert response['statusCode'] == 200
    # Add more assertions based on your Lambda function's expected behavior


def test_lambda_handler_file_not_found(s3_client):
    event = {
        'Records': [{
            'eventName': 'ObjectCreated:Put',
            's3': {
                'bucket': {'name': 'test-bucket'},
                'object': {'key': 'prefix/non-existent-file.txt'}
            }
        }]
    }
    context = {}
    
    response = lambda_handler(event, context)
    
    assert response['statusCode'] == 404
    # Add more assertions for error handling