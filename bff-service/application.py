from flask import Flask, request, Response
import requests

application = Flask(__name__)

INTERNAL_API_URL = "https://cj1fjt38ve.execute-api.eu-north-1.amazonaws.com/development"

@application.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
@application.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
def proxy(path):
    print(f"Received request for path: {path}");
    print(f"Request method: {request.method}");
    print(f"Request headers: {request.headers}")
    print(f"Request cookies: {request.cookies}")
    print(f"Request data len: {len(request.get_data())}")

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