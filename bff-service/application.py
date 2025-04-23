from flask import Flask, request, Response
import requests
import logging
import json
from dotenv import load_dotenv, dotenv_values

application = Flask(__name__)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

INTERNAL_API_URL = "https://cj1fjt38ve.execute-api.eu-north-1.amazonaws.com/development"

@application.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
@application.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def proxy(path):
    logger.info(f"## Received request for path: {path}")
    logger.info(f"## Request method: {request.method}")
    logger.info(f"## Request headers: {json.dumps(request.headers)}")
    logger.info(f"## Request cookies: {json.dumps(request.cookies)}")
    logger.info(f"## Request data len: {len(request.get_data())}")

    # Construct the URL for the internal API
    url = f"{INTERNAL_API_URL}/{path}"

    # Forward the request to the internal API
    resp = requests.request(
        method=request.method,
        url=url,
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)

    # Create a Flask Response object from the API response
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in resp.raw.headers.items()
               if name.lower() not in excluded_headers]

    response = Response(resp.content, resp.status_code, headers)
    return response

if __name__ == '__main__':
    application.run(debug=True)