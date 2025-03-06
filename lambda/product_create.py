# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import json
import logging
import boto3
from botocore.exceptions import ClientError, ParamValidationError
import uuid
from collections import Counter
from decimal import Decimal

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb_client = boto3.client('dynamodb')

def handler(event, context):
    # Response template
    response = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
    }

    # Request body (json)
    body = event['body']
    data = json.loads(body)
   
    # Validate fields
    if Counter(list(data)) != Counter(['title', 'description', 'price', 'count']):
        logger.error(
            "Invalid request data %s ",
            body,
        )
        response['statusCode'] = 400
        response['body'] = json.dumps('Invalid request data')
        return response
    
    # Add uuid
    data['id'] = str(uuid.uuid4())
    logging.info(f"## Raw sourse data: {json.dumps(data)}")
    
    # Validate price
    try:
        data['price'] = Decimal(str(data['price']))
    except:
        return invalidField('price', data, body)
    
    if data['price'] <= 0:
        return invalidField('price', data, body)
    
    # Validate count
    try:
        data['count'] = int(data['count'])
    except:
        return invalidField('count', data, body)
    if data['count'] < 0:
        return invalidField('count', data, body)
    
    # Validate title
    if len(data['title']) < 5 or len(data['title']) > 255:
        return invalidField('title', data, body)

    # Validate description
    if len(data['description']) < 10 or len(data['description']) > 255:
        return invalidField('description', data, body)
    
    try:
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
        logger.error(
            "Couldn't put product model %s into tables %s and %s . Here's why: %s: %s",
            data,
            os.environ.get("TABLE_NAME_PRODUCTS"),
            os.environ.get("TABLE_NAME_STOCKS"),
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        response['statusCode'] = 500
        response['body'] = json.dumps('Error')
        return response
    except ParamValidationError as err:
        logger.error(
            "Couldn't put product model %s into tables %s and %s . Here's why: %s",
            data,
            os.environ.get("TABLE_NAME_PRODUCTS"),
            os.environ.get("TABLE_NAME_STOCKS"),
            err
        )
        response['statusCode'] = 500
        response['body'] = json.dumps('Error')
        return response

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': json.dumps(f"Product is created successfuly. Product url: https://d3eddq2lndvxd8.cloudfront.net/admin/product-form/{data['id']}")
    }


def invalidField(field, data, body):
    logger.error(
        "Invalid %s %s in body %s",
        field,
        data[field],
        body,
    )
    return {
        'statusCode': 400,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': json.dumps(f"Invalid value for field {field}")
    }
