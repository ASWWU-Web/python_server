import tornado.autoreload
import tornado.web
import os
from tornado.options import define

# environment variables
from dotenv import load_dotenv
load_dotenv()

# import settings
from settings import config

from src.aswwu import application


if __name__ == "__main__":
    # TODO: generate env
    if not os.environ['ENVIRONMENT'] or not os.environ['HMAC_KEY'] or not os.environ['SAML_ENDPOINT_KEY']:
        print("Environment variables are not set. Please set them in the .env file.")
        exit(1)
    env = os.environ['ENVIRONMENT']


    # allow command line arguments e.g. `python server.py --port=8881`
    define("port", default=config.server.get('port'), help="run on the given port", type=int)
    define("log_name", default=config.logging.get('log_name'), help="name of the logfile")
    define("current_year", default=config.mask.get('current_year'), help="current school year")
    tornado.options.parse_command_line()


    print("Running in the " + env + " Environment")
    assert env != "pytest"  # the pytest environment should never be used here

    # reload the server if changes are made
    if env == "development":
        tornado.autoreload.start()

    server, event_loop_thread = application.start_server()

    print('services running, press ctrl+c to stop')
    try:
        while True:
            input('')
    except KeyboardInterrupt:
        print('stopping services...')
        application.stop_server(server, event_loop_thread)
        exit(0)
