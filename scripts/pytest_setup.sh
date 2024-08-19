#!/bin/bash
cp config.template.toml config.toml
pip install --upgrade pip
pip install pipenv
pipenv install --ignore-pipfile
pipenv run pip install setuptools
