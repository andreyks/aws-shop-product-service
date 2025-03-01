# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import json
# import logging

# logger = logging.getLogger()
# logger.setLevel(logging.INFO)


def handler(event, context):
    # Temporary store data in the code.
    dummy_products = [
        {
            'id': 1,
            'count': 2,
            'title': 'Peanuts',
            'description': 'Product cdsc long description',
            'price': 5,
        },
        {
            'id': 2,
            'count': 3,
            'title': 'Cashews',
            'description': 'Cashews long description',
            'price': 15,
        },
        {
            'id': 3,
            'count': 4,
            'title': 'Walnuts',
            'description': 'Walnuts long description',
            'price': 5,
        },
        {
            'id': 4,
            'count': 5,
            'title': 'Macadamia',
            'description': 'Product hdfd long description',
            'price': 40,
        },
        {
            'id': 5,
            'count': 2,
            'title': 'Almond',
            'description': 'Almond long description',
            'price': 17,
        },
        {
            'id': 6,
            'count': 2,
            'title': 'Nazelnuts',
            'description': 'Nazelnuts long description',
            'price': 18,
        },
    ]

    response = {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        }
    }

    # Requested product id.
    product_id = event['pathParameters']['product_id']

    if not product_id.isnumeric():
        response['statusCode'] = 404
        response['body'] = json.dumps('Product ID should be a number')
    else:
        product_id = int(product_id)
        if product_id > 0 and product_id <= len(dummy_products):
            response['body'] = json.dumps(dummy_products[product_id-1])   
        else:
            response['statusCode'] = 404
            response['body'] = json.dumps('Product not found')

    return response
