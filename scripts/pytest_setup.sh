#!/bin/bash
cp test_settings.py settings.py
pip install --upgrade pip
pip install pipenv
pipenv install --ignore-pipfile
