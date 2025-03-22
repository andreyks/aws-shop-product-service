import os
import base64
import logging
import json
# from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handler(event, context):
    logger.info(event)
    try:
        authorization_header = event['authorizationToken']

        if not authorization_header:
            logger.error("No authorization header")
            return {
                'statusCode': 401,
                'body': 'Unauthorized',
            }
        
        # Retrieve credentials.
        encodedCreds = authorization_header.split(' ')[1]
        decodedCreds = base64.b64decode(encodedCreds).decode('utf-8')
        username, password = decodedCreds.split('=')
        password = password.strip()
        # load creadential from ENV
        stored_password = os.environ.get(username)

        # Validate credentials.
        logger.info(f"## Username: {username}, Password: {password}, Stored password: {stored_password}")
        if stored_password and stored_password == password:
            return generateAllow(username, event['methodArn'])
        else:
            return generateDeny(username, event['methodArn'])
        
    except Exception as e:
        logger.error(f"## Error: {e}")
        return {
            'statusCode': 500,
            'body': 'Internal Server Error',
        }

def generatePolicy(principalId, effect, resource):
    authResponse = {}
    authResponse['principalId'] = principalId
    if (effect and resource):
        policyDocument = {}
        policyDocument['Version'] = '2012-10-17'
        policyDocument['Statement'] = []
        statementOne = {}
        statementOne['Action'] = 'execute-api:Invoke'
        statementOne['Effect'] = effect
        statementOne['Resource'] = resource
        policyDocument['Statement'] = [statementOne]
        authResponse['policyDocument'] = policyDocument
    return authResponse
    # authResponse_JSON = json.dumps(authResponse)
    # return authResponse_JSON

def generateAllow(principalId, resource):
    return generatePolicy(principalId, 'Allow', resource)


def generateDeny(principalId, resource):
    return {
        'statusCode': 403,
        'body': 'Forbidden',
    }