# The ASWWU Server

![Python application](https://github.com/ASWWU-Web/python_server/workflows/Python%20application/badge.svg) [![codecov](https://codecov.io/gh/ASWWU-Web/python_server/branch/develop/graph/badge.svg)](https://codecov.io/gh/ASWWU-Web/python_server)


## INSTRUCTIONS OUT OF DATE

## Setup

- `pipenv install`
- `cp test_settings.py settings.py`
- in `settings.py`
    - set `testing['dev']` to `True` to bypass authentication
    - set `testing['developer']` to your WWU ID, to make yourself the current user locally.
    - when running pytests
        - set `testing['pytest']` to `True`, and
        - set `testing['dev']` to `False`

If you need to use the current databases, they can be accessed with `scp` 
at the relative path indicated in the `settings.py` file on the server.

## Run in Development

- `pipenv run python server.py`
- test your connection with `curl -X GET http://localhost:8888/search/all`

**Note:** The live server is available at `https://aswwu.com/server/`

# Documentation
The raw documentation files can be found in the docs folder. To view the parsed versions, use the following links:

## Master Branch
- [Elections](https://docs.aswwu.com?url=https://raw.githubusercontent.com/ASWWU-Web/python_server/master/docs/elections.yml)

## Develop Branch
- [Elections](https://docs.aswwu.com?url=https://raw.githubusercontent.com/ASWWU-Web/python_server/develop/docs/elections.yml)
