[![Build Status](https://travis-ci.org/prestoncarman/python_server.svg?branch=develop)](https://travis-ci.org/prestoncarman/python_server)

# REST API for ASWWU
This is a python based REST api that ASWWU web uses for EVERYTHING.

## Installation

**Note:** This uses python 2 so if you don't have that installed, install it [here](https://www.python.org/downloads/).

The following python packages need to be installed and they can be installed with the following command.
```
pip install pattern requests SQLAlchemy tornado bleach
```
You should be ready to run the server now.
```
python server.py
```

## Check Installation
You can test the connection by opening [`http://localhost:8888/search/all`](http://localhost:8888/search/all).

If you see a json array of profiles you're all set. Congrats! You now have a clone of the ASWWU backend server running locally!

## Further usage
If you want get a list of other endpoints(urls) that you can query on the server checkout the `server.py` file in the root of this project.

```python
handlers = [
    (r"/login", base.BaseLoginHandler),
    (r"/profile/(.*)/(.*)", mask.ProfileHandler),
    (r"/profile_photo/(.*)/(.*)", mask.ProfilePhotoHandler),
    (r"/search/all", mask.SearchAllHandler),
    ...
    ]
```
From this array you can see that the function that handles the `/search/all` url is part of the mask module. In `./src/aswwu/route_handlers/mask.py` you can see the function that handles this.
```python
# get all of the profiles in our database
class SearchAllHandler(BaseHandler):
    def get(self):
        profiles = alchemy.query_all(mask_model.Profile)
        self.write({'results': [p.base_info() for p in profiles]})
```

## Testing
We have continuous integration working on this project however it doesn't actually use any of the actual python server code. :( You can run a dummy test by running the following command.
```
pytest
```


## Miscellaneous

If you need it the live server is available at [`https://aswwu.com/server/`](https://aswwu.com/server/).

**Note:** If you having trouble with this process please email [ryan.rabello@wallawalla.edu](mailto:ryan.rabello@wallawalla.edu).
