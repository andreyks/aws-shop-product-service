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
    # Response template
    response = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        }
    }

    # Requested product id.
    product_id = event['pathParameters']['product_id']
    logging.info(f"## Loading product with UUID: {product_id}")
    if not len(product_id) == 36:
        response['statusCode'] = 500
        response['body'] = json.dumps('Given UUID is incorrect')
        return response

    # Load product from DB
    table_name_products = os.environ.get("TABLE_NAME_PRODUCTS")
    table_products = dynamodb.Table(table_name_products)
    try:
        product = table_products.get_item(
            Key={"id": product_id},
        )
        logging.info(f"## Raw product data: {product} from table {table_products.table_name}")
    except ClientError as err:
        logger.error(
            "Couldn't get product %s from table %s. Here's why: %s: %s",
            product_id,
            table_products.table_name,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        response['statusCode'] = 500
        response['body'] = json.dumps('Error')
        return response
    else:
        try:
            product = product["Item"]
        except KeyError:
            logger.error(
                "Product %s is not found in table %s",
                product_id,
                table_products.table_name,
            )
            response['statusCode'] = 404
            response['body'] = json.dumps('Product not found')
            return response
        else:
            product['price'] = str(product['price'])
        
    # Fetch stock data from DB
    table_name_stocks = os.environ.get("TABLE_NAME_STOCKS")
    table_stocks = dynamodb.Table(table_name_stocks)
    try:
        countRow = table_stocks.get_item(
            Key={"id": product_id},
            ProjectionExpression="amount",
        )
        logging.info(f"## Raw stock data: {countRow} from table {table_stocks.table_name}")
        countRow = countRow["Item"]
    except ClientError as err:
        logger.error(
            "Couldn't get stock %s from table %s. Here's why: %s: %s",
            product_id,
            table_stocks.table_name,
            err.response["Error"]["Code"],
            err.response["Error"]["Message"],
        )
        product['count'] = 0
    except KeyError as err:
        logger.error(
            "Missing stock value for product %s from table %s",
            product_id,
            table_stocks.table_name,
        )
        product['count'] = 0
    else:
        product['count'] = str(countRow['amount'])

    response['body'] = json.dumps(product)
    return response
