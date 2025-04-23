#!/bin/bash
#python3 -m venv /var/app/staging/venv
#source /var/app/staging/venv/bin/activate
#pip install -r /var/app/staging/requirements.txt

##!/bin/bash
# Create virtual environment if it doesn't exist
if [ ! -d /var/app/staging/venv ]; then
    python3.11 -m venv /var/app/staging/venv
fi

# Activate virtual environment and install requirements
source /var/app/staging/venv/bin/activate
pip install -r /var/app/staging/requirements.txt