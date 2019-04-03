# The ASWWU Server
## Installation
1. Install pipenv to manage the Python dependencies.
```
$ pip3 install pipenv
```

2. The dependency packages can then be installed with the following command.
```
$ pipenv install
```

3. Setup your MySQL server and database. Create the database with the following MySQL command.
```
mysql> CREATE DATABASE server CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
The server will automatically create the tables on startup

4. You will need to setup a `.env` file. Copy the `.env.sample` file and fill in the appropriate info. Pipenv will
load the environment variables on startup.

## Running
Now run the server by calling.
```
$ pipenv run python server.py
```
You can test the connection by opening `http://localhost:8888/search/all`.

Congrats! You now have a clone of the backend server running locally.

**Note:** The live server is available at `https://aswwu.com/server/`

# Docker
The Tornado web server has been fully containerized and can be used as follows.

## Build
To build the container, use the following command.
```
$ docker build -t aswwu .
```

## Run
To run the container, use the following command.
```
$ docker run -d -p 8888:8888 --env-file .env aswwu:latest
```
You must setup your `.env` file before running the container.

## Push
The pre-built images are stored in the AWS Elastic Container Registry. Commands to setup the AWS CLI and push the container to the registry can be found in the ECR control panel.

# Documentation
The raw documentation files can be found in the docs folder. To view the parsed versions, use the following links:

## Master Branch
- [Elections](https://docs.aswwu.com?url=https://raw.githubusercontent.com/ASWWU-Web/python_server/master/docs/elections.yml)

## Develop Branch
- [Elections](https://docs.aswwu.com?url=https://raw.githubusercontent.com/ASWWU-Web/python_server/develop/docs/elections.yml)
