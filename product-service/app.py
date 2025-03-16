import aws_cdk as cdk
from stacks.product_service_stack import ProductServiceStack

app = cdk.App()
ProductServiceStack(app, "ProductStack")
app.synth()
