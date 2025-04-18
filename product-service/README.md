
# Product service


## Overview

Task 4: Creates an [AWS Lambda](https://aws.amazon.com/lambda/) function writing to [Amazon DynamoDB](https://aws.amazon.com/dynamodb/) and invoked by [Amazon API Gateway](https://aws.amazon.com/api-gateway/) HTTP API.  
![architecture](docs/architecture.png)

Task 6: Create a service to be able to save products which were provided in csv file in database using SQS & SNS.

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

Task 4 demo data import:

```
$ (cd demo_data; sh import.sh)
```

Task 4 create new product with Gateway API:
```
curl -i \
  -X POST https://am2xsc1rw3.execute-api.eu-north-1.amazonaws.com/development/products \
  -H 'Content-Type: application/json' \
  -d '{
    "title": "New test product",
    "description": "New test product  description",
    "price": "23.01",
    "count": "4"
}'
```

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
Deactivate your virtualenv
```
deactivate
```

## Testing

prepare
```
pip install -r requirements-dev.txt 
```
run tests
```
pytest -W ignore::DeprecationWarning -s tests/unit/test_product_by_id.py
pytest -W ignore::DeprecationWarning -s tests/unit/test_product_list.py
pytest -W ignore::DeprecationWarning -s tests/unit/test_catalog_batch_process.py
```

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
