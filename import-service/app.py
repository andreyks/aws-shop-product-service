import aws_cdk as cdk
from stacks.import_service_stack import ImportServiceStack

app = cdk.App()
ImportServiceStack(app, "ImportStack")
app.synth()
