# The ASWWU Server

![Python application](https://github.com/ASWWU-Web/python_server/workflows/Python%20application/badge.svg)

## Run in Development

- `pipenv install`
- `cp .env.example .env`
- `pipenv run python server.py`
- test your connection with `curl -X GET http://localhost:8888/search/all`

if you want to have auto login with your wwu id, the `developer_id` field in the `config.toml` file and restart the server.

**Note:** The live server is available at `https://aswwumask.com/server/`

## Production

- clone the repository
- `cp .env.example .env`
- in `.env`
  - set `ENVIRONMENT=production`
  - update the secret fields
- then run docker compose build
- then run docker compose up

if you need to update config.toml
run `docker-compose down` then `docker-compose up --build`
