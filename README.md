# The ASWWU Server
## Installation
The following python packages need to be installed and they can be installed with the following command.
```
pip install -r requirements.txt
```

Then you need to get a copy of the settings file. To do this, run the following command:
```
scp ./ user@aswwu.com:/data/python_server/settings.py
```
Once you've done this, change the `dev` parameter to `True`, and the `developer` parameter to your WWU ID.

Then you need to get a copy of the database file. Run the following command from the directory one level up from the python server.
```
git clone user@aswwu.com:/data/databases
```
The python library looks for the database file in `../databases` so make sure you clone the database repository into the correct place.

## Running

Now run the server by calling.
```
python server.py
```
You can test the connection by opening `http://localhost:8888/search/all`.

Congrats! You now have a clone of the backend server running locally.

**Note:** The live server is available at `https://aswwu.com/server/`
