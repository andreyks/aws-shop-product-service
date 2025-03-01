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
    table_name = os.environ.get("TABLE_NAME")
    table = dynamodb.Table(table_name)
    logging.info(f"## Loaded table name from environemt variable DDB_TABLE: {table}") 

    body = table.scan()
    body = body["Items"]
    print("ITEMS----")
    print(body)

    responseBody = []
    for items in body:
        responseItems = [
            {'price': float(items['price']), 
             'id': items['id'], 
             'name': items['name'],
             'description': items['description']
            }]
        responseBody.append(responseItems)
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': json.dumps(responseBody)
    }
