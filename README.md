# The ASWWU Server
## Installation
The following python packages need to be installed and they can be installed with the following command.
```
./scripts/startup.sh
```

Then you need to get a copy of the settings file. To do this, run the following command:
```
scp user@<server_ip>:/data/python_server/settings.py ./
```
Once you've done this, change the `dev` parameter to `True`, and the `developer` parameter to your WWU ID is 
settings.py.

Then you need to get a copy of the database files. Run the following command from the directory one level up from the 
python server.
```
scp user@<server_ip>:/data/databases ./
```
The python library looks for the database file referenced in settings.py as `database['location']` so make sure you clone the database repository into 
the correct place.

## Running

Now run the server by calling.
```
python server.py
```
You can test the connection by opening `http://localhost:8888/search/all`.

Congrats! You now have a clone of the backend server running locally.

**Note:** The live server is available at `https://aswwu.com/server/`

# Documentation
The raw documentation files can be found in the docs folder. To view the parsed versions, use the following links:

## Master Branch
- [Elections](https://docs.aswwu.com?url=https://raw.githubusercontent.com/ASWWU-Web/python_server/master/docs/elections.yml)

## Develop Branch
- [Elections](https://docs.aswwu.com?url=https://raw.githubusercontent.com/ASWWU-Web/python_server/develop/docs/elections.yml)
