
import os
import logging
import tornado.escape
import tornado.ioloop
import tornado.web
import tornado.autoreload
from tornado.options import define, options

from alchemy.base_handlers import *

define("port", default=8888, help="run on the given port", type=int)
define("log_name", default="pyserver", help="name of the logfile")
define("auth_url", default="/auth")

class Application(tornado.web.Application):
    def __init__(self):
        settings = {
            "cookie_secret": "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            "login_url": "/login"
        }

        handlers = [
            (r"/login", LoginHandler),
            (r"/", IndexHandler),
        ]

        self.options = options
        logger = logging.getLogger("pyserver")
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler("etc/logs/"+options.log_name+".py")
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter("{'timestamp': %(asctime)s, 'loglevel' : %(levelname)s %(message)s }")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        tornado.web.Application.__init__(self, handlers, **settings)
        logger.info("Application started on port " + str(options.port))


if __name__ == "__main__":
    config = tornado.options.parse_command_line()
    if len(config) == 0:
        conf_name = "default"
    else:
        conf_name = config[0]
    io_loop = tornado.ioloop.IOLoop.instance()
    tornado.options.parse_config_file("etc/conf/"+conf_name+".conf")
    application = Application()
    application.listen(options.port)
    tornado.autoreload.start()
    io_loop.start()
