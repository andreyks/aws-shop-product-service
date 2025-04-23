# BFF (backend for frontend)


## Overview

Task 10  (BFF)

## Setup

Copy `env.example` as `.env` and put there valid credentials.

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


## Deploy with Elastic Beanstalks

```
% eb init -p python-3.11 -r eu-north-1 bff
```

```
% eb create devbff --cname andreyks-bff --single --timeout 25
```


## Cleanup 
Run below script to delete AWS resources created by this sample stack.
```
eb terminate devbff
```
Deactivate your virtualenv
```
deactivate
```
