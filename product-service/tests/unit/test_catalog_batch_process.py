import os
import boto3
import pytest
import unittest
import json
from moto import mock_aws
import sys
# Add the lambda directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'lambda')))
from catalog_batch_process import handler as lambda_handler

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
def dynamodb(aws_credentials):
    with mock_aws():
        yield boto3.client('dynamodb', region_name = AWS_REGION)

@pytest.fixture(scope='function')
def create_tables(dynamodb):
    dynamodb.create_table(
        TableName='test_products',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )
    dynamodb.create_table(
        TableName='test_stocks',
        KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )

@pytest.fixture(scope='function')
def sns(aws_credentials):
    with mock_aws():
        yield boto3.client('sns', region_name = AWS_REGION)

@pytest.fixture(scope='function')
def create_topic(sns):
    topic = sns.create_topic(Name='create-product-topic')
    topic_arn = topic['TopicArn']
    return topic_arn

def test_transact_write_items(dynamodb, create_tables, sns, create_topic):
    os.environ['SNS_TOPIC_ARN'] = create_topic

    # Test data
    data = {
        'id': 'test_uuid',
        'title': 'Test Product',
        'description': 'This is a test product',
        'price': 19.99,
        'count': 100
    }

    # Prepare test event
    event = {
        'Records': [
            {
                'body': json.dumps({
                    'id': data['id'],
                    'title': data['title'],
                    'description': data['description'],
                    'price': data['price'],
                    'count': data['count'],
                })
            }
        ]
    }

    # Execute the function
    lambda_handler(event, None)

    # Check if items were added to the tables
    products_item = dynamodb.get_item(
        TableName='test_products',
        Key={'id': {'S': data['id']}}
    )
    assert 'Item' in products_item
    assert products_item['Item']['title']['S'] == data['title']

    stocks_item = dynamodb.get_item(
        TableName='test_stocks',
        Key={'id': {'S': data['id']}}
    )
    assert 'Item' in stocks_item
    assert stocks_item['Item']['amount']['N'] == str(data['count'])

    # Check if the product was added to DynamoDB with another function
    items = list(dynamodb.scan(TableName='test_products')['Items'])
    assert len(items) == 1
    assert items[0]['title']['S'] == data['title']

    # Check if a message was published to SNS
    topics = sns.list_topics()
    assert len(topics['Topics']) == 1
