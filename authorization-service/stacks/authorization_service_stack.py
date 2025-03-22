import os
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_apigatewayv2_authorizers as authorizers,
    aws_apigatewayv2 as apigwv2,
    CfnOutput,
)
from constructs import Construct
from dotenv import load_dotenv, dotenv_values

load_dotenv()

class AuthorizationServiceStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create the Lambda function for the authorizer
        authorizer_lambda = _lambda.Function(
            self, "AuthorizerFunction",
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler="basic_authorization.handler",
            code=_lambda.Code.from_asset("lambda"),
            environment=dotenv_values('.env'),
            # environment={
            #     'andreyks': os.getenv('andreyks'),
            # },
        )
        CfnOutput(self, "AuthorizerLambdaArn", value=authorizer_lambda.function_arn, export_name='AuthorizerLambdaArn')
