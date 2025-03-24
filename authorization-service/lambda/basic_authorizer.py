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
        # Authorization Header
        if not ('authorizationToken' in event and event['authorizationToken']):
            logger.error("No authorization header")
            # return 'unauthorized'
            return {
                'statusCode': 401,
                'body': json.dumps({'message': 'No authorization header'}),
            }
            # return generateDeny(username, event['methodArn'])
        authorization_header = event['authorizationToken'] # event['identitySource'][0] for SIMPLE
        logger.info(authorization_header)
        
        # Retrieve token.
        token = authorization_header.split(' ')
        if not (token[0] == 'Basic' and len(token) == 2 and token[1]):
            logger.error("Invalid authorization header")
            # return 'unauthorized'
            return {
                'statusCode': 401,
                'body': json.dumps({'message': 'Invalid authorization header'}),
            }
            # return generateDeny(username, event['methodArn'])
        token = token[1]
        logger.info(token)

        # Credentials.
        decodedCreds = base64.b64decode(token).decode('utf-8')
        logger.info(decodedCreds)
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
        return 'unauthorized'
        # return {
        #     'statusCode': 500,
        #     'body': 'Custom Internal Server Error',
        # }

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
    logger.info(f"## Allow: principalId: {resource}, resource: {resource}")
    return generatePolicy(principalId, 'Allow', resource)


def generateDeny(principalId, resource):
    logger.info(f"## Deny: principalId: {resource}, resource: {resource}")
    response = generatePolicy(principalId, 'Deny', resource)
    response['context'] = {
        'message': 'Access denied: invalid credentials',
    }
    return response
    # return {
    #     'statusCode': 403,
    #     'body': 'Forbidden',
    # }
