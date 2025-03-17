import aws_cdk as core
import aws_cdk.assertions as assertions

from stacks.product_service_stack import ProductServiceStack


def test_sqs_queue_created():
    app = core.App()
    stack = ProductServiceStack(app, "product-service-stack")
    template = assertions.Template.from_stack(stack)

