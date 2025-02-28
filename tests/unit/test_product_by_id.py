import json
import unittest
from unittest.mock import patch
import sys
import os

# Add the lambda directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'lambda')))

from product_by_id import handler

def test_handler():
    # Arrange
    event = {
        "httpMethod": "GET",
        "path": "/product/123",
        "pathParameters": {
            "product_id": "2"
        }
    }
    context = {}

    # Act
    response = handler(event, context)

    # Assert
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'price' in body
    assert body['id'] == 2
