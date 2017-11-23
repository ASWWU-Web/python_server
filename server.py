# server.py
import threading

import tornado.ioloop
from tornado.options import define

import application


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
    io_loop = tornado.ioloop.IOLoop(make_current=False).instance()
    tornado.options.parse_config_file("src/aswwu/"+conf_name+".conf")

    # create thread for running the server
    thread = threading.Thread(target=application.start_server, args=(tornado, io_loop))
    thread.daemon = True
    thread.start()

    print 'services running, press ctrl+c to stop'
    try:
        while True:
            raw_input('')
    except KeyboardInterrupt:
        print 'stopping services...'
        application.stop_server(io_loop)
        exit(0)
