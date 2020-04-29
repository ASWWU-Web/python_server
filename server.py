import tornado.autoreload
import tornado.web
from tornado.options import define

from settings import testing, production
from src.aswwu import application

if __name__ == "__main__":
    # allow command line arguments e.g. `python server.py --port=8881`
    define("port", default=production['port'], help="run on the given port", type=int)
    define("log_name", default=production['log_name'], help="name of the logfile")
    define("current_year", default=production['current_year'], help="current school year")
    tornado.options.parse_command_line()

    # reload the server if changes are made
    if testing['dev']:
        tornado.autoreload.start()

    server, event_loop_thread, ioloop = application.start_server()

    print 'services running, press ctrl+c to stop'
    try:
        while True:
            raw_input('')
    except KeyboardInterrupt:
        print 'stopping services...'
        application.stop_server(server, event_loop_thread, ioloop)
        exit(0)
