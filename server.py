from __future__ import print_function
from builtins import input
import tornado.autoreload
import tornado.web
from tornado.options import define

from settings import environment
from src.aswwu import application

if __name__ == "__main__":
    # allow command line arguments e.g. `python server.py --port=8881`
    define("port", default=environment["port"], help="run on the given port", type=int)
    define("log_name", default=environment["log_name"], help="name of the logfile")
    define("current_year", default=environment["current_year"], help="current school year")
    tornado.options.parse_command_line()

    print("Running in the " + environment["environment_name"] + " Environment")
    assert environment["pytest"] == False  # the pytest environment should never be used here

    # reload the server if changes are made
    if environment["dev"]:
        tornado.autoreload.start()

    server, event_loop_thread, ioloop = application.start_server()

    print('services running, press ctrl+c to stop')
    try:
        while True:
            input('')
    except KeyboardInterrupt:
        print('stopping services...')
        application.stop_server(server, event_loop_thread, ioloop)
        exit(0)
