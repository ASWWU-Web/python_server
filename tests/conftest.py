import time
import pytest
import tornado.options
import threading
import utils
import settings
import os
from tornado.ioloop import IOLoop

assert os.environ["ENVIRONMENT"] == "pytest" # make sure the pytest environment has been set

tornado.options.define("port", default=settings.config.server.get('port'))
tornado.options.define("log_name", default=settings.config.logging.get('log_name'))
tornado.options.define("current_year", default=settings.config.mask.get('current_year'))

utils.clean_temporary_folder()
utils.setup_databases()

# TODO: (riley) fix tests
@pytest.fixture()
def testing_server():
    pass
    # # TODO: (stephen) find a way to copy fresh databases on every run without causing IO errors
    utils.reset_databases()
    utils.clean_temporary_folder(folder_path=settings.buildMediaPath("profile_pictures"))

    # for now, we are manually threading the server until i can figure out the asyncio stuff
    server, event_loop_thread = start_server()
    yield
    stop_server(server, event_loop_thread)

def start_server():
    # application must be imported after databases are setup
    from src.aswwu.application import Application
    application = Application()
    server = application.listen(tornado.options.options.port)

    # TODO: move this to asyncio
    event_loop_thread = threading.Thread(target=IOLoop.current().start)
    event_loop_thread.daemon = True
    event_loop_thread.start()
    print('The Tornado IOLoop thread has started.')
    return server, event_loop_thread

def stop_server(server, event_loop_thread):
    server.stop()
    IOLoop.current().add_callback(IOLoop.current().stop)
    event_loop_thread.join()