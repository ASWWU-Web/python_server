import time
import pytest
import tornado.options
import threading
import utils
import settings

assert settings.environment["pytest"]  # make sure the pytest environment has been set

tornado.options.define("port", default=settings.environment["port"], type=int)
tornado.options.define("log_name", default=settings.environment["log_name"])
tornado.options.define("current_year", default=settings.environment["current_year"])

utils.clean_temporary_folder()
utils.setup_databases()

@pytest.fixture()
def testing_server():
    # TODO: (stephen) find a way to copy fresh databases on every run without causing IO errors
    utils.reset_databases()
    utils.clean_temporary_folder(folder_path=settings.environment["profile_photos_location"])

    # application must be imported after databases are setup
    from src.aswwu.application import start_server, stop_server

    server, event_loop_thread, ioloop = start_server()
    yield
    stop_server(server, event_loop_thread, ioloop)
