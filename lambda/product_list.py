# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

import os
import json
# import logging

# logger = logging.getLogger()
# logger.setLevel(logging.INFO)


def handler(event, context):
    dummy_products = [
        {
            'id': 1,
            'count': 2,
            'title': 'Peanuts',
            'description': f'Product cdsc long description',
            'price': 5,
        },
        {
            'id': 2,
            'count': 3,
            'title': 'Cashews',
            'description': f'Cashews long description',
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
            'description': f'Nazelnuts long description',
            'price': 18,
        },
    ]
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': json.dumps(dummy_products)
    }
