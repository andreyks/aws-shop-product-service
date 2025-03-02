# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import json
import logging
import boto3
from botocore.exceptions import ClientError
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")

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
    # TODO: validate input

    data['id'] = str(uuid.uuid4())
    logging.info(f"## Raw sourse data: {data}")

    # Write product data
    try:
        product_data = {
            'price': data['price'],
            'id': data['id'],
            'title': data['title'],
            'description': data['description'],
        }
        table_name_products = os.environ.get("TABLE_NAME_PRODUCTS")
        table_products = dynamodb.Table(table_name_products)
        body = table_products.put_item(Item=product_data)
        logging.info(f"## Raw product response: {body} from table {table_products.table_name}")
    except ClientError as err:
        logger.error(
            "Couldn't put data %s into table table %s . Here's why: %s: %s",
            product_data,
            table_products.table_name,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        response['statusCode'] = 500
        response['body'] = json.dumps('Error')
        return response
    
    # Write stock data
    try:
        stock_data = {
            'id': data['id'],
            'amount': data['count'],
        }
        table_name_stocks = os.environ.get("TABLE_NAME_STOCKS")
        table_stocks = dynamodb.Table(table_name_stocks)
        body = table_stocks.put_item(Item=stock_data)
        logging.info(f"## Raw stocks response: {body} from table {table_stocks.table_name}")
    except ClientError as err:
        logger.error(
            "Couldn't put data %s into table table %s . Here's why: %s: %s",
            stock_data,
            table_stocks.table_name,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        response['statusCode'] = 500
        response['body'] = json.dumps('Error')
        return response
    
    # Retrieve new product with stock data
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': json.dumps(f"Product is created successfuly. Product url: https://d3eddq2lndvxd8.cloudfront.net/admin/product-form/{data['id']}")
    }
