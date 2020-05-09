import time
import pytest
import tornado.options
import threading

import utils
# from settings import database, testing
from settings import environment

assert environment["pytest"]  # make sure the pytest environment has been set

tornado.options.define("port", default=environment["port"], type=int)
tornado.options.define("log_name", default=environment["log_name"])
tornado.options.define("current_year", default=environment["current_year"])

utils.setup_temp_databases(environment['original_testing_databases'], environment['databases_location'])


@pytest.fixture()
def testing_server():
    utils.reset_databases()

    # application must be imported after databases are setup
    from src.aswwu.application import start_server, stop_server

    server, event_loop_thread, ioloop = start_server()
    yield
    stop_server(server, event_loop_thread, ioloop)
