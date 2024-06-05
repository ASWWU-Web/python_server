# The ASWWU Server

![Python application](https://github.com/ASWWU-Web/python_server/workflows/Python%20application/badge.svg) [![codecov](https://codecov.io/gh/ASWWU-Web/python_server/branch/develop/graph/badge.svg)](https://codecov.io/gh/ASWWU-Web/python_server)

## Run in Development

- `pipenv install`
- `cp test_settings.py settings.py`
- in `settings.py`

  - set `testing['dev']` to `True` to bypass authentication
  - set `testing['developer']` to your WWU ID, to make yourself the current user locally.
  - set environment to `local_dev_environment`
  - when running pytests
    - set `testing['pytest']` to `True`, and
    - set `testing['dev']` to `False`

- `pipenv run python server.py`
- test your connection with `curl -X GET http://localhost:8888/search/all`

**Note:** The live server is available at `https://aswwumask.com/server/`

## Production

- clone the repository
- `cp test_settings.py settings.py`
- in `settings.py`
  - set `environment = production_environment`
  - update any settings needed such as `database` and `secret_key`
- then run docker compose build
- then run docker compose up

if you need to update settings.py
run `docker-compose down` then `docker-compose up --build`

# Documentation

The raw documentation files can be found in the docs folder. To view the parsed versions, use the following links:

## Master Branch

- [Elections](https://docs.aswwu.com?url=https://raw.githubusercontent.com/ASWWU-Web/python_server/master/docs/elections.yml)

## Develop Branch

- [Elections](https://docs.aswwu.com?url=https://raw.githubusercontent.com/ASWWU-Web/python_server/develop/docs/elections.yml)
