import time
import pytest
import tornado.ioloop
from tornado.options import options, define

from src.aswwu import application


def start_testing_server():
    conf_file = "tests/default.conf"
    define("port", type=int)
    define("log_name")
    define("current_year")
    tornado.options.parse_config_file(conf_file)

    server = application.start_server()

    # give the server time to start before running tests
    time.sleep(1)

    return server


def stop_testing_server(server):
    application.stop_server(server)


@pytest.fixture()
def testing_server():
    server = start_testing_server()
    yield
    stop_testing_server(server)
