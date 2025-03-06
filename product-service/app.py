'''
Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
SPDX-License-Identifier: MIT-0
'''

import aws_cdk as cdk
from stacks.apigw_http_cdk_stack import ApigwHttpCdkStack

app = cdk.App()
ApigwHttpCdkStack(app, "ApigwHttpCdkStack")
app.synth()
