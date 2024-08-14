import time
import pytest
import tornado.options
import threading
import utils
import settings
import os

assert os.environ["ENVIRONMENT"] == "pytest" # make sure the pytest environment has been set

settings.loadConfig("./config.testing.toml")

tornado.options.define("port", default=settings.config["port"], type=int)
tornado.options.define("log_name", default=settings.config["log_name"])
tornado.options.define("current_year", default=settings.config["current_year"])

utils.clean_temporary_folder()
utils.setup_databases()

# TODO: (riley) fix tests
@pytest.fixture()
def testing_server():
    pass
    # # TODO: (stephen) find a way to copy fresh databases on every run without causing IO errors
    utils.reset_databases()
    utils.clean_temporary_folder(folder_path=settings.buildMediaPath("profile_pictures"))

    # application must be imported after databases are setup
    from src.aswwu.application import start_server, stop_server

    server, event_loop_thread = start_server()
    yield
    stop_server(server, event_loop_thread)
