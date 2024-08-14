#!/bin/bash
ENVIRONMENT=pytest pipenv run pytest --cov-report=xml --cov=src tests/
