#!/bin/bash
pip install --upgrade pip
pip install pipenv
pipenv install --ignore-pipfile
pipenv run pip install setuptools
