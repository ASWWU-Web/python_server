import time
import pytest
import tornado.ioloop
from tornado.options import options, define
import threading

from src.aswwu.application import start_server, stop_server
from utils import replace_databases
from settings import database, testing


define("port", default=testing['port'], type=int)
define("log_name", default=testing['log_name'])
define("current_year", default=testing['current_year'])

temp_databases_path = testing['database'] + '/temp_dbs'
database['location'] = temp_databases_path
testing['dev'] = False

@pytest.fixture()
def testing_server():
    replace_databases(testing['database'], temp_databases_path)
    server, event_loop_thread = start_server()
    yield
    stop_server(server, event_loop_thread)
