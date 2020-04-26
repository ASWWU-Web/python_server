#!/bin/bash
pipenv run pytest --cov-report=xml --cov=src tests/
