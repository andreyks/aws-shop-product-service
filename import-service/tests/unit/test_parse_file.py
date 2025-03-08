import pytest
import boto3
from moto import mock_aws
import sys
import os
import botocore

# Import your Lambda function
# Add the lambda directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'lambda')))
from parse_file import handler as lambda_handler


@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['BUCKET_NAME'] = 'test_bucket'

@pytest.fixture
def s3_client(aws_credentials):
    with mock_aws():
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket=os.environ['BUCKET_NAME'])
        s3.put_object(Bucket=os.environ['BUCKET_NAME'], Key='uploaded/test-file.csv', Body="name,surname\nAndrii,Kostromin")
        yield s3

def test_lambda_handler(s3_client):
    event = {
        'Records': [{
            'eventName': 'ObjectCreated:Put',
            's3': {
                'bucket': {'name': os.environ['BUCKET_NAME']},
                'object': {'key': 'uploaded/test-file.csv'}
            }
        }]
    }
    context = {}
    
    # Call the Lambda function with the mock event
    lambda_handler(event, context)

    # Assert that the file was processed as expected
    # For example, if your function copies the file to a new location:
    try:
        s3_client.head_object(Bucket=os.environ['BUCKET_NAME'], Key='parsed/test-file.csv')
        file_exists = True
    except:
        file_exists = False
    
    assert file_exists, "Processed file should exist in the destination location"

    # Assert that the original file was deleted
    with pytest.raises(s3_client.exceptions.ClientError) as e:
        s3_client.head_object(Bucket=os.environ['BUCKET_NAME'], Key='uploaded/test-file.csv')
    assert e.value.response['Error']['Code'] == '404'
