# server.py

import tornado.autoreload
import tornado.ioloop
import tornado.web
from tornado.options import define, options

from src.application import Application
from settings import testing


if __name__ == "__main__":
    # allow command line arguments e.g. `python server.py --port=8881`
    define("port", default=8888, help="run on the given port", type=int)
    define("log_name", default="aswwu", help="name of the logfile")
    define("current_year", default="1920", help="current school year")
    tornado.options.parse_command_line()

    io_loop = tornado.ioloop.IOLoop.instance()

    application = Application()
    application.start_server()

    # reload the server if changes are made
    if testing['dev']:
        tornado.autoreload.start()
    io_loop.start()
