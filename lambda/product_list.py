# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import json
import logging
import boto3
import uuid

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")

def handler(event, context):
    table_name_products = os.environ.get("TABLE_NAME_PRODUCTS")
    table_products = dynamodb.Table(table_name_products)
    logging.info(f"## Loaded table name from environemt variable DB_TABLE_PRODUCTS: {table_products.table_name}") 

    body = table_products.scan()
    items = body["Items"]
    print("PRODUCTS----")
    print(items)


    table_name_stocks = os.environ.get("TABLE_NAME_STOCKS")
    table_stocks = dynamodb.Table(table_name_stocks)
    logging.info(f"## Loaded table name from environemt variable DB_TABLE_STOCKS: {table_stocks.table_name}") 

    body = table_stocks.scan()
    items2 = body["Items"]
    print("STOCKS----")
    print(items2)

    response = {}
    for item in items:
        response[item['id']] = {
            'price': float(item['price']), 
            'id': item['id'], 
            'title': item['title'],
            'description': item['description'],
        }

    for item2 in items2:
        response[item2['id']].update({'count': int(item2['count'])})
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': json.dumps(list(response.values()))
    }
