#!/bin/bash

# run after Python3.7 is setup

# pycairo and PyGObject dependencies
apt install libcairo2-dev pkg-config python3-dev gcc libgirepository1.0-dev
apt install xvfb

# isntall virtualenv if it's not already
pip3 install virtualenv --user

# create virtual env, activate it, and install dependencies
virtualenv -p python3 venv
. venv/bin/activate
pip3 install -r requirements.txt