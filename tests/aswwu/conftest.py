import pytest

import threading

import tornado.ioloop
from tornado.options import define
import application


def start_testing_server():
    # pass in the conf default name
    conf_name = "default"

    # initiate the IO loop for Tornado
    io_loop = tornado.ioloop.IOLoop.instance()
    tornado.options.parse_config_file("src/aswwu/" + conf_name + ".conf")

    # create thread for running the server
    thread = threading.Thread(
        target=application.start_server, args=(tornado, io_loop))
    thread.daemon = True
    thread.start()

    # allow server to start before running tests
    import time
    time.sleep(1)
    print('starting services...')
    return (io_loop, thread)


def stop_testing_server(io_loop, thread):
    application.stop_server(io_loop)
    thread.join()


@pytest.fixture()
def testing_server():
    (io_loop, thread) = start_testing_server()
    yield
    stop_testing_server(io_loop, thread)
