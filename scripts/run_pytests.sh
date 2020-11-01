#!/bin/bash

# PYTHON 2
# pipenv run pytest --cov-report=xml --cov=src tests/

# PYTHON 3
pipenv run python3 -m pytest --cov-report html --cov tests/ 