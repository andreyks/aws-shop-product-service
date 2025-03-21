import os
import json
import boto3
import logging
from botocore.exceptions import ClientError, ParamValidationError
import uuid
from collections import Counter
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    # Retrieve the messages from the SQS event
    messages = event['Records']
    logging.info(f"Messages: {messages}")
    
    # Process each message in the batch
    for message in messages:
        # Retrieve the JSON message body
        message_body = json.loads(message['body'])
        logging.info(f"Raw row data: {message['body']}")

        try:
            validateProduct(message_body)
            saveProduct(message_body)
            notify(message_body)
        except Exception as e:
            logging.error(repr(e) + f". Raw row data: {message['body']}")
            continue

def validateProduct(data):
    # Validate uuid. Generate UUID for the record if it is missing
    if not data.get('id'):
        data['id'] = str(uuid.uuid4())

    # Validate fields
    if Counter(list(data)) != Counter(['id', 'title', 'description', 'price', 'count']):
        raise ValueError('Invalid request field set')

    # Validate price
    try:
        data['price'] = Decimal(str(data['price']))
    except:
        raise ValueError(f"Invalid value {data['price']} of field price")
    
    if data['price'] <= 0:
        raise ValueError(f"Invalid value {data['price']} of field price")
    
    # Validate count
    try:
        data['count'] = int(data['count'])
    except:
        raise ValueError(f"Invalid value {data['count']} of field count")
    if data['count'] < 0:
        raise ValueError(f"Invalid value {data['count']} of field count")
    
    # Validate title
    if len(data['title']) < 5 or len(data['title']) > 255:
        raise ValueError(f"Invalid value {data['title']} of field title")

    # Validate description
    if len(data['description']) < 10 or len(data['description']) > 255:
        raise ValueError(f"Invalid value {data['description']} of field description")

def saveProduct(data):
    try:
        # Initialize the DynamoDB client
        dynamodb_client = boto3.client('dynamodb')
        response = dynamodb_client.transact_write_items(
            TransactItems=[
                {
                    'Put': {
                        'TableName': os.environ.get("TABLE_NAME_PRODUCTS"),
                        'Item': {
                            'id': {'S': data['id']},
                            'title': {'S': data['title']},
                            'description': {'S': data['description']},
                            'price': {'N': str(data['price'])}
                        }
                    }
                },
                {
                    'Put': {
                        'TableName': os.environ.get("TABLE_NAME_STOCKS"),
                        'Item': {
                            'id': {'S': data['id']},
                            'amount': {'N': str(data['count'])},
                        }
                    }
                }
            ]
        )
        logging.info(f"## Transaction response: {json.dumps(response)}")
    except ClientError as err:
        raise Exception(f"Save product ClientError: {err.response["Error"]["Code"]}: {err.response["Error"]["Message"]}.")
    except ParamValidationError as err:
        raise Exception(f"Save product ParamValidationError {err}.")

def notify(message):
    price = float(message.get('price', 0))

    # Send a single email notification about all products imported in current batch
    sns_client = boto3.client('sns')
    sns_client.publish(
        TopicArn=os.environ['SNS_TOPIC_ARN'],
        Subject='New products creation',
        Message = f"Product is added to database: {message}",
        MessageAttributes={
            'price': {
                'DataType': 'Number',
                'StringValue': str(price)
            }
        }
    )
    logging.info(f"Notify product with price {str(price)}: {message}")
