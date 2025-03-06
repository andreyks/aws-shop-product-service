import aws_cdk as core
import aws_cdk.assertions as assertions

from stacks.apigw_http_cdk_stack import ApigwHttpCdkStack


def test_sqs_queue_created():
    app = core.App()
    stack = ApigwHttpCdkStack(app, "apigw-http-api-lambda-dynamodb-python-cdk")
    template = assertions.Template.from_stack(stack)

