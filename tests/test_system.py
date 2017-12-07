# test_system.py
import requests
import json


def test_root(testing_server):
    expected_data = {
        "username": "ryan.rabello",
        "wwuid": "919428746",
        "roles": "forms-admin",
        "photo": "profiles/1718/00958-2019687.jpg",
        "status": None,
        "full_name": "Ryan Rabello"
    }

    url = 'http://127.0.0.1:8888/'
    resp = requests.get(url)
    assert (resp.status_code == 200)
    assert (json.loads(resp.text) == expected_data)


def test_search_all(testing_server):
    expected_data = {
        "results": [{
            "username": "john.doe",
            "photo": "profiles/1718/00958-2019687.jpg",
            "email": "",
            "full_name": "John Doe",
            "views": "6"
        }, {
            "username": "ryan.rabello",
            "photo": "profiles/1718/00958-2019687.jpg",
            "email": "ryan.rabello@wallawalla.edu",
            "full_name": "Ryan Rabello",
            "views": "9"
        }, {
            "username": "jane.anderson",
            "photo": "profiles/1718/00958-2019687.jpg",
            "email": "",
            "full_name": "Jane Anderson",
            "views": "8"
        }, {
            "username": "michael.scott",
            "photo": "None",
            "email": "None",
            "full_name": "Michael Scott",
            "views": "0"
        }, {
            "username": "mary.johnson",
            "photo": "profiles/1718/00958-2019687.jpg",
            "email": "",
            "full_name": "Mary Johnson",
            "views": "6"
        }, {
            "username": "susan.brown",
            "photo": "profiles/1718/00958-2019687.jpg",
            "email": "",
            "full_name": "Susan Brown",
            "views": "18"
        }]
    }

    url = 'http://127.0.0.1:8888/search/all'
    resp = requests.get(url)
    assert (resp.status_code == 200)
    assert (json.loads(resp.text) == expected_data)
