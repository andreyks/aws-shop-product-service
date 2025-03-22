import aws_cdk as cdk
from stacks.authorization_service_stack import AuthorizationServiceStack

app = cdk.App()
AuthorizationServiceStack(app, "AuthorizationStack")
app.synth()
