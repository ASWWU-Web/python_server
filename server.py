# server.py

import tornado.autoreload
import tornado.ioloop
import tornado.web
from tornado.options import define, options

from application import Application
from settings import testing

# import handlers as needed - here we import all of them

# define some initial options that can be passed in at run time
# e.g. `python server.py --port=8881` would run the server on port 8881
define("port", default=8888, help="run on the given port", type=int)
define("log_name", default="aswwu", help="name of the logfile")
define("current_year", default="1920")


# the main class that wraps everything up nice and neat


# running `python server.py` actually tells python to rename this file as "__main__"
# hence this check to make sure we actually wanted to run the server
if __name__ == "__main__":
    # pass in the conf name with `python server.py CONF_NAME`
    # by default this is "default"
    config = tornado.options.parse_command_line()
    if len(config) == 0:
        conf_name = "default"
    else:
        conf_name = config[0]

    # initiate the IO loop for Tornado
    io_loop = tornado.ioloop.IOLoop.instance()
    tornado.options.parse_config_file("src/aswwu/"+conf_name+".conf")
    # create a new instance of our Application
    application = Application()
    application.listen(options.port)
    # tell it to autoreload if anything changes
    if testing['dev']:
        tornado.autoreload.start()
    io_loop.start()
