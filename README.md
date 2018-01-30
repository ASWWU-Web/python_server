# Le python backend
## Installation
The following python packages need to be installed and they can be installed with the following command.
```
pip install -r requirements.txt
```

Then you need to get a copy of the database file. In your git projects folder run the following command
```
git clone user@aswwu.com:/data/databases
```
The python library looks for the database file in `../databases` so make sure you clone the database repository into the correct place.

**Note:** This git repo is also used for daily backups to the actual database.

Now run the server by calling.
```
python server.py
```
You can test the connection by opening `http://localhost:8888/search/all`.

Congrats! You now have a clone of the backend server running locally.

**Note:** The live server is available at `https://aswwu.com/server/`
