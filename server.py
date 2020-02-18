import tornado.autoreload
import tornado.web
from tornado.options import define

from settings import testing
from src.aswwu import application

if __name__ == "__main__":
    # allow command line arguments e.g. `python server.py --port=8881`
    define("port", default=8888, help="run on the given port", type=int)
    define("log_name", default="aswwu", help="name of the logfile")
    define("current_year", default="1920", help="current school year")
    tornado.options.parse_command_line()

    # reload the server if changes are made
    if testing['dev']:
        tornado.autoreload.start()

    server, event_loop_thread = application.start_server()

    print 'services running, press ctrl+c to stop'
    try:
        while True:
            raw_input('')
    except KeyboardInterrupt:
        print 'stopping services...'
        application.stop_server(server, event_loop_thread)
        exit(0)
