# test_system.py
import pytest
import unittest
import requests
import json

import logging
import threading

import tornado.ioloop
from tornado.options import define, options

import application

def start_testing_server():
    # pass in the conf default name
    conf_name = "default"

    # initiate the IO loop for Tornado
    global io_loop
    io_loop = tornado.ioloop.IOLoop.instance()
    tornado.options.parse_config_file("src/aswwu/"+conf_name+".conf")

    # create thread for running the server
    thread = threading.Thread(target=application.start_server, args=(tornado, io_loop))
    thread.daemon = True
    thread.start()

    # allow server to start before running tests
    import time
    time.sleep(1)
    print('starting services...')

def stop_testing_server():
    application.stop_server(io_loop)

class test_system(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        start_testing_server()
        print("setup_class()")

    @classmethod
    def teardown_class(cls):
        stop_testing_server()
        print("teardown_class()")

    def test_root(self):
        expected_data = {
                "username": "ryan.rabello",
                "wwuid": "919428746",
                "roles": "",
                "photo": "profiles/1718/00958-2019687.jpg",
                "status": None,
                "full_name": "Ryan Rabello"
            }

        url = 'http://127.0.0.1:8888/'
        resp = requests.get(url)
        assert(resp.status_code == 200)
        assert(json.loads(resp.text) == expected_data)

    def test_search_all(self):
        expected_data = {
                "results": [
                        {"username": "john.doe", "photo": "profiles/1718/00958-2019687.jpg", "email": "", "full_name": "John Doe", "views": "6"},
                        {"username": "ryan.rabello", "photo": "profiles/1718/00958-2019687.jpg", "email": "ryan.rabello@wallawalla.edu", "full_name": "Ryan Rabello", "views": "9"},
                        {"username": "jane.anderson", "photo": "profiles/1718/00958-2019687.jpg", "email": "", "full_name": "Jane Anderson", "views": "8"},
                        {"username": "michael.scott", "photo": "None", "email": "None", "full_name": "Michael Scott", "views": "0"},
                        {"username": "mary.johnson", "photo": "profiles/1718/00958-2019687.jpg", "email": "", "full_name": "Mary Johnson", "views": "6"},
                        {"username": "susan.brown", "photo": "profiles/1718/00958-2019687.jpg", "email": "", "full_name": "Susan Brown", "views": "18"}
                ]
        };

        url = 'http://127.0.0.1:8888/search/all'
        resp = requests.get(url)
        assert(resp.status_code == 200)
        assert(json.loads(resp.text) == expected_data)
