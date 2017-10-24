# test_server.py
# Start the normal server
import os
import logging
import tornado.escape
import tornado.ioloop
import tornado.web
import tornado.autoreload
from tornado.options import define, options

# import handlers as needed - here we import all of them
from aswwu.base_handlers import *
from aswwu.route_handlers import *

# import our super secret keys
from settings import keys

#Import the Server Applciation
from server import Application

def setup_module(module):
    # pass in the conf name with `python server.py CONF_NAME`
    # by default this is "default"
    config = tornado.options.parse_command_line()
    if len(config) == 0:
        conf_name = "default"
    else:
        conf_name = config[0]

    # initiate the IO loop for Tornado
    io_loop = tornado.ioloop.IOLoop.instance()
    tornado.options.parse_config_file("aswwu/"+conf_name+".conf")
    # create a new instance of our Application
    application = Application()
    application.listen(options.port)
    # tell it to autoreload if anything changes
    tornado.autoreload.start()
    io_loop.start()

def teardown_module(module):
    io_loop.stop()

# Begin testing

# a Dummy test.
def func(x):
    return x + 1

def test_answer():
    assert func(3) == 4
