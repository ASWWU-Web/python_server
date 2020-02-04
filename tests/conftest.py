import threading

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

    io_loop = tornado.ioloop.IOLoop.instance()
    thread = threading.Thread(
        target=application.start_server, args=(io_loop,))
    thread.daemon = True
    thread.start()

    # give the server time to start before running tests
    import time
    time.sleep(1)
    return io_loop, thread


def stop_testing_server(io_loop, thread):
    application.stop_server(io_loop)
    thread.join()


@pytest.fixture()
def testing_server():
    io_loop, thread = start_testing_server()
    yield
    stop_testing_server(io_loop, thread)
