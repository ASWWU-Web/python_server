import time
import pytest
import tornado.ioloop
from tornado.options import options, define
import threading

from src.aswwu.application import Application, start_server, stop_server
from settings import testing

define("port", default=testing['port'], type=int)
define("log_name", default=testing['log_name'])
define("current_year", default=testing['current_year'])
tornado.options.parse_command_line()
options_defined = True


@pytest.fixture()
def testing_server():
    server, event_loop_thread = start_server()
    yield
    stop_server(server, event_loop_thread)
