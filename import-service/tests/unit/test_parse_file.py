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

AWS_REGION = 'us-east-1'
FILE_NAME = 'data.csv'

@pytest.fixture
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = AWS_REGION
    """Environment Variables"""
    os.environ['BUCKET_NAME'] = 'test_bucket'
    os.environ['QUEUE_URL'] = 'https://sqs.us-east-1.amazonaws.com/140023362000/ProductStack-catalogItemsQueue79451959-KSbsUwvv0Pto'

@pytest.fixture
def s3_client(aws_credentials):
    with mock_aws():
        s3 = boto3.client('s3')
        s3.create_bucket(Bucket=os.environ['BUCKET_NAME'])
        s3.put_object(Bucket=os.environ['BUCKET_NAME'], Key=f"uploaded/{FILE_NAME}", Body="name,surname\nAndrii,Kostromin")
        yield s3

def test_lambda_handler(s3_client):
    event = {
        'Records': [{
            'eventName': 'ObjectCreated:Put',
            's3': {
                'bucket': {'name': os.environ['BUCKET_NAME']},
                'object': {'key': f"uploaded/{FILE_NAME}"}
            }
        }]
    }
    context = {}
    
    # Call the Lambda function with the mock event
    lambda_handler(event, context)

    # Assert that the file was processed as expected
    # For example, if your function copies the file to a new location:
    try:
        s3_client.head_object(Bucket=os.environ['BUCKET_NAME'], Key=f"parsed/{FILE_NAME}")
        file_exists = True
    except:
        file_exists = False
    
    assert file_exists, "Processed file should exist in the destination location"

    # Assert that the original file was deleted
    with pytest.raises(s3_client.exceptions.ClientError) as e:
        s3_client.head_object(Bucket=os.environ['BUCKET_NAME'], Key=f"uploaded/{FILE_NAME}")
    assert e.value.response['Error']['Code'] == '404'
