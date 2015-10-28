
import os
import logging
import tornado.escape
import tornado.ioloop
import tornado.web
from tornado.options import define, options

from handlers import *

define("port", default=8888, help="run on the given port", type=int)
define("log_path", default="./pyserver.log", help="path to logfile")


class Application(tornado.web.Application):
    def __init__(self):
        settings = {}

        handlers = [
            (r"/", IndexHandler),
        ]

        logger = logging.getLogger("pyserver")
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(options.log_path)
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter("{'timestamp': %(asctime)s, 'loglevel' : %(levelname)s %(message)s }")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        tornado.web.Application.__init__(self, handlers, **settings)
        logger.info("Application started on port " + str(options.port))


if __name__ == "__main__":
    config = tornado.options.parse_command_line()
    io_loop = tornado.ioloop.IOLoop.instance()

    tornado.options.parse_config_file("settings.conf")
    application = Application()

    application.listen(options.port)
    io_loop.start()
