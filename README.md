
# AWS API Gateway HTTP API to AWS Lambda


## Overview

Creates an [AWS Lambda](https://aws.amazon.com/lambda/) function and invoked by [Amazon API Gateway](https://aws.amazon.com/api-gateway/) HTTP API. 

![architecture](docs/architecture.png)

## Setup

The `cdk.json` file tells the CDK Toolkit how to execute your app.

This project is set up like a standard Python project.  The initialization
process also creates a virtualenv within this project, stored under the `.venv`
directory.  To create the virtualenv it assumes that there is a `python3`
(or `python` for Windows) executable in your path with access to the `venv`
package. If for any reason the automatic creation of the virtualenv fails,
you can create the virtualenv manually.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Deploy
At this point you can deploy the stack. 

Using the default profile

```
$ cdk deploy
```

With specific profile

```
$ cdk deploy --profile test
```


## Cleanup 
Run below script to delete AWS resources created by this sample stack.
```
cdk destroy
```

## Testing

prepare
```
pip install -r requirements-dev.txt 
```
run tests
```
pytest -s tests/unit/test_product_by_id.py
pytest -s tests/unit/test_product_list.py
```

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!

Useful links:
Swagger file preview https://editor.swagger.io/
AWS API Gateway HTTP API to AWS Lambda in VPC to DynamoDB CDK Python Sample! https://github.com/aws-samples/aws-cdk-examples/tree/2599de6c9c1ce489ff74e67c39e8df213c1c55ec/python/apigw-http-api-lambda-dynamodb-python-cdk
AWS APIGatewayv2 Construct  https://docs.aws.amazon.com/cdk/api/v2/python/aws_cdk.aws_apigatewayv2/README.html
Tutorial: Create a CRUD HTTP API with Lambda and DynamoDB https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-dynamo-db.html#http-api-dynamo-db-create-function
