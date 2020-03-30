import time
import pytest
import tornado.ioloop
from tornado.options import options, define
import threading

from src.aswwu.application import Application, start_server, stop_server

conf_file = "tests/default.conf"
define("port", type=int)
define("log_name")
define("current_year")
tornado.options.parse_config_file(conf_file)
options_defined = True


@pytest.fixture()
def testing_server():
    server, event_loop_thread = start_server()
    yield
    stop_server(server, event_loop_thread)
