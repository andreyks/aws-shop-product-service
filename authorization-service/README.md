
# Product service


## Overview

Task 7  (Authorization)

## Setup

Copy `.env.example` as `.env` and put there valid credentials.

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

## Testing

Set valid auth token. Please type in browser JS console with valid user name:
```
const token = btoa('vasiapupkin=TEST_PASSWORD'); localStorage.setItem('authorization_token', token)
```

Testing with curl (please put valid credentials):
```
# 200 (OK)
curl -v -H "Authorization: Basic $(echo -n "vasiapupkin=TEST_PASSWORD" | base64)"  "https://jbuqseyfkg.execute-api.eu-north-1.amazonaws.com/development/import?name=data.csv"

# 403 (wrong username/password)
curl -v -H "Authorization: Basic $(echo -n "vasiapupkin=TEST_PASSWOR" | base64)"  "https://jbuqseyfkg.execute-api.eu-north-1.amazonaws.com/development/import?name=data.csv"
curl -v -H "Authorization: Basic $(echo -n "vasiapupkin=" | base64)"  "https://jbuqseyfkg.execute-api.eu-north-1.amazonaws.com/development/import?name=data.csv"

# 500 (wrong Authorization header format)
curl -v -H "Authorization: Basic $(echo -n "vasiapupkin" | base64)"  "https://jbuqseyfkg.execute-api.eu-north-1.amazonaws.com/development/import?name=data.csv"
curl -v -H "Authorization: $(echo -n "vasiapupkin=TEST_PASSWORD" | base64)"  "https://jbuqseyfkg.execute-api.eu-north-1.amazonaws.com/development/import?name=data.csv"

# 401 (missing Authorization header)
curl -v "https://jbuqseyfkg.execute-api.eu-north-1.amazonaws.com/development/import?name=data.csv"
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

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!
