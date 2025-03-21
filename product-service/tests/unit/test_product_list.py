import boto3
import pytest
from moto import mock_aws
import sys
import os

# Add the lambda directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'lambda')))

from product_list import handler

AWS_REGION = 'us-east-1'

@pytest.fixture(scope='function')
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'
    os.environ['AWS_DEFAULT_REGION'] = AWS_REGION
    """Environment Variables"""
    os.environ['TABLE_NAME_PRODUCTS'] = 'test_products'
    os.environ['TABLE_NAME_STOCKS'] = 'test_stocks'

@pytest.fixture(scope='function')
def dynamodb_client(aws_credentials):
    with mock_aws():
        yield boto3.client('dynamodb', region_name = AWS_REGION)

@pytest.fixture(scope='function')
def dynamodb(aws_credentials):
    with mock_aws():
        yield boto3.resource('dynamodb', region_name = AWS_REGION)

@pytest.fixture(scope='function')
def create_tables(dynamodb_client):
    dynamodb_client.create_table(
        TableName='test_products',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )
    dynamodb_client.create_table(
        TableName='test_stocks',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )

@pytest.fixture(scope='function')
def demo_data(dynamodb_client, create_tables):
    # Initialize the DynamoDB client
    data = [
        {
            'id': 'test_uuid',
            'title': 'Test Product',
            'description': 'This is a test product',
            'price': 19.99,
            'count': 100
        }, 
        {
            'id': 'test_uuid_2',
            'title': 'Test Product 2',
            'description': 'This is a test product 2',
            'price': 23,
            'count': 18
        }, 
    ]

    for item in data:
        response = dynamodb_client.transact_write_items(
            TransactItems=[
                {
                    'Put': {
                        'TableName': os.environ.get("TABLE_NAME_PRODUCTS"),
                        'Item': {
                            'id': {'S': item['id']},
                            'title': {'S': item['title']},
                            'description': {'S': item['description']},
                            'price': {'N': str(item['price'])}
                        }
                    }
                },
                {
                    'Put': {
                        'TableName': os.environ.get("TABLE_NAME_STOCKS"),
                        'Item': {
                            'id': {'S': item['id']},
                            'amount': {'N': str(item['count'])},
                        }
                    }
                }
            ]
        )
        print(response)

    return data

@mock_aws
def test_handler(dynamodb, demo_data):
    # Prepare
    event = {}
    context = {}

    # Act
    response = handler(event, context)
    

    # Assert
    assert response['statusCode'] == 200
    body = response['body']
    print (body)
    assert demo_data[0]['title'] in body
