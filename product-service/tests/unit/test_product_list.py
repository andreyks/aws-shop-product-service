import json
import unittest
from unittest.mock import patch
import sys
import os

# Add the lambda directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'lambda')))

from product_list import handler

def test_handler():
    # Prepare
    event = {}
    context = {}

    # Act
    response = handler(event, context)

    # Assert
    assert response['statusCode'] == 200
    body = response['body']
    assert 'Peanuts' in body
