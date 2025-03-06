# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import json
import logging
import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")

def handler(event, context):
    # Load product data
    try:
        table_name_products = os.environ.get("TABLE_NAME_PRODUCTS")
        table_products = dynamodb.Table(table_name_products)
        body = table_products.scan()
        logging.info(f"## Raw products data: {body} from table {table_products.table_name}")
    except ClientError as err:
        logger.error(
            "Couldn't load from table %s . Here's why: %s: %s",
            table_products.table_name,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        items=[]
    else:
        try:
            items = body["Items"]
        except KeyError:
            logger.error("No results from table %s", table_products.table_name)
            items=[]
            
    # Load stocks information
    try:
        table_name_stocks = os.environ.get("TABLE_NAME_STOCKS")
        table_stocks = dynamodb.Table(table_name_stocks)
        body = table_stocks.scan()
        logging.info(f"## Raw stocks data: {body} from table {table_stocks.table_name}")
    except ClientError as err:
        logger.error(
            "Couldn't load from table %s . Here's why: %s: %s",
            table_stocks.table_name,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        stocks=[]
    else:
        try:
            stocks = body["Items"]
        except KeyError:
            logger.error("No results from table %s", table_stocks.table_name)
            stocks=[]


    # Process product data
    response = {}
    for item in items:
        response[item['id']] = {
            'price': float(item['price']),
            'id': item['id'],
            'title': item['title'],
            'description': item['description'],
        }

    # Process stock data
    for stock in stocks:
        response[stock['id']].update({'count': int(stock['amount'])})
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': json.dumps(list(response.values()))
    }
